from random import random

import spirecomm.spire.powers.powers as p
import spirecomm.spire.card
from spirecomm.ai import combatSim


# TODO: where to put this?
# TODO: implement powers.apply

def draw(n):
    combatSim.draw(n)

class SimCard:

    @classmethod
    def play(cls, card, target=None):
        cls.target = target
        cls.cost = card.cost
        cls.upgrades = card.upgrades
        card_method = card.card_id.replace(" ", "_")
        globals()[card_method]()


    def damage(self, base, add):
        """
        Takes in card information and deals damage, taking into account on-damage effects and upgrades.
        int base: base (unupgraded) damage of card
        int add: amount to add per upgrade (always max 1 except searing blow)
        source: source of dmg (player or monster)
        target: target (player or monster) receiving damage
        upgrades: number of upgrades (always 0 or 1 except searing blow)
        """
        # adjust damage for buffs/debuffs (strength, weakness, vuln, etc.)
        self.target.current_hp -= base + self.upgrades*add - self.target.block
        # source.onReceiveDamage
        # target.onDealDamage (?)

    def damage_all(self, base, add):
        for t in self.target:
            t.current_hp -= base + self.upgrades*add

    def block(self, base, add):
        self.target.block += (base + self.upgrades*add)

    def discard(self, index=-1):
        """
        Discard a card in target (player)'s hand.
        index: if -1, random card, else the card at location index
        """
        player = self.target
        if index >= 0:
            player.hand.pop(index)
        else:
            player.hand.pop(random.randint(0, len(player.hand)-1))

    def get_shiv(self):
        # TODO: implement getShiv
        pass

    def poison(self, base, add):
        self.target.poison += (base + self.upgrades*add)

    def Strike_B(self):
        self.damage(6, 3)

    def Defend_B(self):
        self.block(6, 3)

    def Neutralize(self):
        self.damage(4, 2)
        p.apply("weakened", self.target)

    def Survivor(self):
        self.block(8, 3)
        self.discard(-1)

    def Acrobatics(self):
        draw(3)
        self.discard(self.target)  # self.target is the chosen card to discard here

    def Backflip(self):
        self.block(5,3)
        draw(2)

    def Bane(self):
        self.damage(7,3)
        if self.target.poison > 0:
            self.damage(7,3)

    def Blade_Dance(self):
        for _ in range(2):
            self.get_shiv()

    def Cloak_And_Dagger(self):
        self.block(6,0)
        for _ in range(self.upgrades + 1):
            self.get_shiv()

    def Dagger_Spray(self):
        for _ in range(2):
            self.damage_all(4, 2)

    def Dagger_Throw(self):
        self.damage(9,3)
        draw(1)
        self.discard(1)

    def Deadly_Poison(self):
        self.poison(5,2)

    def Deflect(self):
        self.block(4,3)

    def Dodge_And_Roll(self):
        self.block(4,2)
        # TODO: dodge_and_roll power
        p.apply("dodge_and_roll", self.target, 4+2*self.upgrades)

    def Flying_Knee(self):
        self.damage(8,3)
        p.apply("next_energy", self.target, 1)

    def Outmaneuver(self):
        # TODO: next_energy power
        p.apply("next_energy", self.target, 2+self.upgrades)

    def Piercing_Wail(self):
        # TODO: strength power
        p.applyAll("strength", -(6+2*self.upgrades))

    def Poisoned_Stab(self):
        self.damage(6,2)
        self.poison(3,1)

    def Prepared(self):
        draw(1+self.upgrades)
        self.discard(1+self.upgrades)

    def Quick_Slash(self):
        self.damage(8,4)
        draw(1)

    def Slice(self):
        self.damage(5,8)

    def Sneaky_Strike(self):
        self.damage(10, 4)
        if player.discarded_this_turn:
            # TODO: energy power
            p.apply("energy", player, 2)

    def Sucker_Punch(self):
        self.damage(7,2)
        # TODO: weakend power
        p.apply("weakened", self.target, 1+self.upgrades)

    def Accuracy(self):
        # TODO: accuracy power
        p.apply("accuracy", self.target, self.upgrades)

    def All_Out_Attack(self):
        self.damage_all(10, 4)
        self.discard()

    def Backstab(self):
        self.damage(11, 4)

    def Blur(self):
        self.block(5,3)
        # TODO: blur power
        p.apply("blur", self.target)

    def Bouncing_Flask(self):
        pass
