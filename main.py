import itertools
import datetime
import sys
import json

from spirecomm.communication.action import PlayCardAction, EndTurnAction
from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass
import random

from spirecomm.ai.combatSim import CombatSim
from spirecomm.ai.mcts import MCTS
from spirecomm.spire.game import Game

if __name__ == "__main__":
    # with open("jawworm.json") as file:
    #     example = json.load(file)
    #     game_state = example['game_state']
    # game = Game.from_json(example.get('game_state'),example.get('available_commands'))
    # # state = game.game_state
    # state = {
    #     'player': game.player,
    #     'deck': game.deck,
    #     'relics': game.relics,
    #     'potions': game.potions,
    #     'hand': game.hand,
    #     'draw_pile': game.draw_pile,
    #     'discard_pile': game.discard_pile,
    #     'exhaust_pile': game.exhaust_pile,
    #     'monsters': game.monsters,
    #     'turn': game.turn
    # }
    # sim = CombatSim(state)
    # mcts = MCTS(sim)
    # agent = SimpleAgent()
    # coordinator = Coordinator()
    # for i in range(100):
    #     mcts = MCTS(sim)
    #     action = mcts.get_action()
    #     playable_cards = [card for card in game.hand if card.is_playable]
    #     if len(playable_cards) == 0:
    #         EndTurnAction().execute(coordinator)
    #
    #     card_to_play = random.choice(playable_cards)
    #     if card_to_play.has_target:
    #         available_monsters = [monster for monster in game.monsters if
    #                               monster.current_hp > 0 and not monster.half_dead and not monster.is_gone]
    #         if len(available_monsters) == 0:
    #             EndTurnAction().execute(coordinator)
    #         target = random.choice(available_monsters)
    #         PlayCardAction(card_index=game.hand.index(card_to_play), target_monster=target).execute(coordinator)
    #         sim.play(card_to_play, target.monster_index)
    #         sim.finish_turn()
    #     else:
    #         PlayCardAction(card_index=game.hand.index(card_to_play)).execute(coordinator)
    #         sim.play(card_to_play, -1)
    #         sim.finish_turn()
    # card = action[0]
    # target = action[1]
    # card_index = sim.hand.index(card)
    # agent = SimpleAgent()
    # coordinator = Coordinator()
    # if card.has_target:
    #     PlayCardAction(card_index=card_index, target_index=target).execute(coordinator)
    # else:
    #     PlayCardAction(card_index=card_index).execute(coordinator)

    # #
    # sim = CombatSim(state)
    # mcts = MCTS(sim)
    #
    # for i in range(100):
    #     if sim.is_over():
    #         print("sim over")
    #         break
    #     mcts.change_state(sim.get_state())
    #     print(sim.player.current_hp, sim.monsters[0].current_hp)
    #     action = mcts.get_action()
    #     card = action[0]
    #     target = action[1]
    #     card_index = sim.hand.index(card)
    #     if card.has_target:
    #         sim.play(card, target)
    #         coordinator.send_message("{} {} {}".format("play", card_index, target))
    #         sim.do_monster_actions()
    #     else:
    #         sim.play(card, -1)
    #         coordinator.send_message("{} {}".format("play", card_index))
    #         sim.do_monster_actions()

    agent = SimpleAgent()
    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)
    agent.change_class(PlayerClass.THE_SILENT)
    result = coordinator.play_one_game(PlayerClass.THE_SILENT)




    # Play games forever, cycling through the various classes
    # for chosen_class in itertools.cycle(PlayerClass):
    #     # agent.change_class(chosen_class)


    # ------------- FOR GUI

    # communicating = True
    # while communicating:
    #     print("hello")
    #     message = input()
    #     coordinator.send_message(message)
