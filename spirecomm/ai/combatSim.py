from random import random

from spirecomm.spire.card import Card
from spirecomm.spire.relic import Relic
from spirecomm.spire.character import Character
from spirecomm.spire.character import Monster
from spirecomm.spire.character import Player
from spirecomm.spire.potion import Potion
from spirecomm.spire import cards


class CombatSim:

    def __init__(self, game_state, numIter):
        self.player = Player.from_json(game_state)
        self.deck = [Card.from_json(c) for c in game_state['deck']]
        self.relics = [Relic.from_json(r) for r in game_state['relics']]
        self.potions = [Potion.from_json(p) for p in game_state['potions']]
        combat_state = game_state['combat_state']
        self.hand = [Card.from_json(c) for c in combat_state['hand']]
        self.draw_pile = [Card.from_json(c) for c in combat_state['draw_pile']]
        self.discard_pile = []
        self.exhaust_pile = []
        self.monsters = [Monster.from_json(m) for m in combat_state['monsters']]

    def step_one_turn(self):
        self.do_player_action()
        self.end_player_turn()
        self.do_monster_actions()
        self.end_monster_turn()
        self.begin_turn()

    def do_player_action(self):
        available = [c for c in self.hand if self.player.can_play(c)]
        cardToPlay = available.choice()

    def do_monster_actions(self):
        pass

    def end_player_turn(self):
        pass

    def end_monster_turn(self):
        for m in self.monsters:
            m.on_end_turn()

    def sim_combat(self):
        while self.player.current_hp >= 0 and all(m.current_hp >= 0 for m in self.monsters):
            self.step_one_turn()

    def begin_turn(self):
        self.draw(5)
        for r in self.relics:
            r.on_start_turn() #TODO: implement
        self.player.on_start_turn()
        for m in self.monsters:
            m.on_start_turn()

    def draw(self, n):
        if n == 0:
            pass
        elif self.hand.length == 10:
            self.draw_pile.pop()
        else:
            if self.draw_pile.length < n:
                self.draw_pile = self.draw_pile.append(self.discard_pile)
                random.shuffle(self.draw_pile)
            self.hand.append(self.draw_pile.pop())
            self.draw(n-1)
