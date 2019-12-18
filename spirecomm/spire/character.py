from enum import Enum
import random

from spirecomm.spire.move_info import MoveInfo, Intent
from spirecomm.spire.power import Power
from spirecomm.spire.powers import SimPower


class PlayerClass(Enum):
    IRONCLAD = 1
    THE_SILENT = 2
    DEFECT = 3


class Orb:

    def __init__(self, name, orb_id, evoke_amount, passive_amount):
        self.name = name
        self.orb_id = orb_id
        self.evoke_amount = evoke_amount
        self.passive_amount = passive_amount

    @classmethod
    def from_json(cls, json_object):
        name = json_object.get("name")
        orb_id = json_object.get("id")
        evoke_amount = json_object.get("evoke_amount")
        passive_amount = json_object.get("passive_amount")
        orb = Orb(name, orb_id, evoke_amount, passive_amount)
        return orb


class Character:

    def __init__(self, max_hp, current_hp=None, block=0):
        self.max_hp = max_hp
        self.current_hp = current_hp
        if self.current_hp is None:
            self.current_hp = self.max_hp
        self.block = block
        self.powers = []
        self.sim_powers = {"strength": 0, "dexterity": 0, "focus": 0, "artifact": 0, "poison": 0}

    def on_start_turn(self):
        for p in self.sim_powers:
            SimPower.on_start_turn(p, self)

    def on_end_turn(self):
        for p in self.sim_powers:
            SimPower.end_of_turn(p, self)

    def on_card_play(self):
        for p in self.sim_powers:
            SimPower.on_card_play(p, self)

    def affected_by(self, key):
        if key in self.sim_powers and not (self.sim_powers[key]["intensity"] <= 0 and self.sim_powers[key]["duration"] <= 0):
            return True
        return False


class Player(Character):

    def __init__(self, max_hp, current_hp=None, block=0, energy=0):
        super().__init__(max_hp, current_hp, block)
        self.energy = energy
        self.orbs = []
        # self.hand = hand

    @classmethod
    def from_json(cls, json_object):
        # print(json_object.keys())
        # player_object = json_object["combat_state"]["player"]
        # print(player_object)
        player = cls(json_object["max_hp"], json_object["current_hp"], json_object["block"], json_object["energy"])
        player.powers = [Power.from_json(json_power) for json_power in json_object["powers"]]
        # player.orbs = [Orb.from_json(orb) for orb in json_object["orbs"]]
        return player

    def can_play(self, card):
        return True if self.energy >= card.cost and card.is_playable else False


class Monster(Character):

    def __init__(self, name, monster_id, max_hp, current_hp, block, intent, half_dead, is_gone, move_id=-1, last_move_id=None, second_last_move_id=None, move_base_damage=0, move_adjusted_damage=0, move_hits=0):
        super().__init__(max_hp + 5, current_hp + 5, block)
        self.name = name
        self.monster_id = monster_id
        self.intent = intent
        self.half_dead = half_dead
        self.is_gone = is_gone
        self.move_id = move_id
        self.last_move_id = last_move_id
        self.second_last_move_id = second_last_move_id
        self.move_base_damage = move_base_damage
        self.move_adjusted_damage = move_adjusted_damage
        self.move_hits = move_hits

        self.move_info = MoveInfo(self)
        #
        # if "Louse" in name and max_hp == current_hp:
        #     block_amt = random.randint(3, 7)
        #     self.powers["curl up"]["intensity"] = block_amt

    @classmethod
    def from_json(cls, json_object):
        name = json_object["name"]
        monster_id = json_object["id"]
        max_hp = json_object["max_hp"]
        current_hp = json_object["current_hp"]
        block = json_object["block"]
        intent = Intent[json_object["intent"]]
        half_dead = json_object["half_dead"]
        is_gone = json_object["is_gone"]
        move_id = json_object.get("move_id", -1)
        last_move_id = json_object.get("last_move_id", None)
        second_last_move_id = json_object.get("second_last_move_id", None)
        move_base_damage = json_object.get("move_base_damage", 0)
        move_adjusted_damage = json_object.get("move_adjusted_damage", 0)
        move_hits = json_object.get("move_hits", 0)
        monster = cls(name, monster_id, max_hp, current_hp, block, intent, half_dead, is_gone, move_id, last_move_id, second_last_move_id, move_base_damage, move_adjusted_damage, move_hits)
        monster.powers = [Power.from_json(json_power) for json_power in json_object["powers"]]
        return monster

    def get_move_from_possible(self, possible_moves):
        if not isinstance(possible_moves[0], str):
            probs = [x.prob for x in possible_moves[0]]
            return random.choices(possible_moves[0], probs)

    def get_move_name_by_id(self, num):
        moves = MoveInfo.MOVE_IDS[self.name]
        for key in moves:
            if moves[key] == num:
                return key

    def move_at_limit(self, move):
        """Returns True if the move cannot be used because if hit its limit (e.g. 2 in a row), False otherwise."""
        move_id = MoveInfo.MOVE_IDS[self.name][move.name]
        if self.last_move_id == move:
            if self.second_last_move_id == move_id:
                return move.limit <= 2
            return move.limit == 1
        return False

    def split(self):
        if self.name == "Acid Slime (L)":
            name = "Acid Slime (M)"
            id = "AcidSlime_M"
        elif self.name == "Spike Slime (L)":
            name = "Spike Slime (L)"
            id = "SpikeSlime_L"
        m1 = Monster(name, id, self.max_hp//2, self.current_hp//2, 0, Intent.NONE, self.half_dead, False)
        m2 = Monster(name, id, self.max_hp//2, self.current_hp//2, 0, Intent.NONE, self.half_dead, False)
        return [m1, m2]

    def __eq__(self, other):
        if self.name == other.name and self.current_hp == other.current_hp and self.max_hp == other.max_hp and self.block == other.block:
            # if self.powers == other.powers:
            #     return True
            # return False
            if len(self.powers) == len(other.powers):
                for i in range(len(self.powers)):
                    if self.powers[i] != other.powers[i]:
                        return False
                return True
        return False

    def __hash__(self):
        return hash(self.monster_id)
