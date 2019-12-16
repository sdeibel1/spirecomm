import itertools
import datetime
import sys
import json

from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass
import random

from spirecomm.ai.combatSim import CombatSim
from spirecomm.ai.mcts import MCTS

if __name__ == "__main__":
    # with open("jawworm.json") as file:
    #     example = json.load(file)
    #     game_state = example['game_state']
    # sim = CombatSim.from_json(game_state)
    # mcts = MCTS(sim)
    # while not sim.is_over():
    #     action = mcts.get_action()
    #     result = sim.sim_combat(action[0], action[1])
    # print(result)
    # print()
    # available_cards = [c for c in sim.hand if sim.player.can_play(c)]
    # card_to_play = random.choice(available_cards)
    # target = random.choice(sim.monsters) if card_to_play.has_target else None
    # sim.sim_combat(card_to_play, target)


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
