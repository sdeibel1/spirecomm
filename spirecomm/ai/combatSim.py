from random import random

from spirecomm.spire.card import Card, CardType, CardRarity
from spirecomm.spire.relic import Relic
from spirecomm.spire.character import Character
from spirecomm.spire.character import Monster
from spirecomm.spire.character import Player
from spirecomm.spire.potion import Potion
from spirecomm.spire import cards
from spirecomm.spire.powers.powers import SimPower as p


class CombatSim:

    player = Player()
    deck = []
    relics = []
    potions = []
    hand = []
    draw_pile = []
    discard_pile = []
    exhaust_pile = []
    monsters = []

    def __init__(self, game_state, numIter):
        self.target = None
        self.upgrades = 0
        self.cost = 0
        self.discard_count = 0
        self.attack_count = 0
        self.glass_knife_count = 0

    @classmethod
    def change_state(cls, game_state):
        combat_state = game_state['combat_state']
        cls.player = Player.from_json(game_state)
        cls.deck = [Card.from_json(c) for c in game_state['deck']]
        cls.relics = [Relic.from_json(r) for r in game_state['relics']]
        cls.potions = [Potion.from_json(p) for p in game_state['potions']]
        cls.hand = [Card.from_json(c) for c in combat_state['hand']]
        cls.draw_pile = [Card.from_json(c) for c in combat_state['draw_pile']]
        cls.discard_pile = []
        cls.exhaust_pile = []
        cls.monsters = [Monster.from_json(m) for m in combat_state['monsters']]

    def step_one_turn(self):
        self.do_player_action()
        self.end_player_turn()
        self.do_monster_actions()
        self.end_monster_turn()
        self.begin_turn()

    def do_player_action(self):
        available = [c for c in self.hand if self.player.can_play(c)]
        card_to_play = available.choice()

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

    def play(self, card, target):
        self.target = target
        self.cost = card.cost
        self.upgrades = card.upgrades
        card_method = card.card_id.replace(" ", "_")
        getattr(CombatSim, card_method)()

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

    def damage(self, base, add, source=None):
        """
        Takes in card information and deals damage, taking into account on-damage effects and upgrades.
        int base: base (unupgraded) damage of card
        int add: amount to add per upgrade (always max 1 except searing blow)
        source: source of dmg (player or monster)
        target: target (player or monster) receiving damage
        upgrades: number of upgrades (always 0 or 1 except searing blow)
        """
        # TODO: adjust damage for buffs/debuffs (strength, weakness, vuln, etc.)
        if source is None:
            source = self.player
        amt = base + self.upgrades * add + source.powers['strength']
        if source.powers['weakened']:
            amt *= .75
        if self.target.powers['vulnerable']:
            amt *= 1.5
        self.target.current_hp -= base + self.upgrades * add - self.target.block
        # source.onReceiveDamage
        # target.onDealDamage (?)

    def damage_all(self, base, add):
        source = self.player
        amt = base + source.powers['strength']
        if source.powers['weakened']:
            amt *= .75
        for t in self.target:
            # TODO: adjust damage for buffs/debuffs (strength, weakness, vuln, etc.)
            if self.target.powers['vulnerable']:
                amt *= 1.5
            self.target.current_hp -= amt + self.upgrades * add - self.target.block

    def block(self, base, add):
        amt = base + self.upgrades * add + self.player.powers['dexterity']
        self.target.block += amt

    def discard(self, n=1, index=-1, card=None):
        """
        Discard a card in target (player)'s hand.
        index: if -1, random card, else the card at location index
        """
        if card:
            self.hand.pop(card)
            return

        if n >= len(self.hand):
            self.discard_count += len(self.hand)
            self.hand = []
        if n > 1:
            new_hand = []
            for i in range(len(self.hand)) not in index:
                new_hand.append(self.hand[i])
            self.hand = new_hand
            self.discard_count += n
        else:
            if index >= 0:
                self.hand.pop(index)
            else:
                self.hand.pop(random.randint(0, len(self.hand) - 1))
            self.discard_count += 1

    def get_shiv(self, upgrades):
        shiv = Card("Shiv", "Shiv", CardType.ATTACK, CardRarity.BASIC, upgrades=upgrades, is_playable=True, exhausts=True)
        self.hand.append(shiv)


    def poison(self, base, add):
        self.target.powers['poison'] += (base + self.upgrades * add)

    # CARDS

    def Strike_G(self):
        self.damage(6, 3)

    def Defend_G(self):
        self.block(6, 3)

    def Neutralize(self):
        self.damage(4, 2)
        p.apply("weak", self.target, duration=1+self.upgrades)

    def Survivor(self):
        self.block(8, 3)
        self.discard(-1)

    def Acrobatics(self):
        self.draw(3)
        self.discard(self.target)  # self.target is the chosen card to discard here

    def Backflip(self):
        self.block(5,3)
        self.draw(2)

    def Bane(self):
        self.damage(7,3)
        if self.target.powers['poison'] > 0:
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
        self.draw(1)
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
        p.apply("next_energy", self.target, duration=1, intensity=1)

    def Outmaneuver(self):
        # TODO: next_energy power
        p.apply("next_energy", duration=1, intensity=2)

    def Piercing_Wail(self):
        # TODO: strength power
        p.apply_all("strength_temp", -(6+2*self.upgrades))

    def Poisoned_Stab(self):
        self.damage(6, 2)
        self.poison(3, 1)

    def Prepared(self):
        self.draw(1+self.upgrades)
        self.discard(1+self.upgrades)

    def Quick_Slash(self):
        self.damage(8, 4)
        self.draw(1)

    def Slice(self):
        self.damage(5, 8)

    def Sneaky_Strike(self):
        self.damage(10, 4)
        if self.player.discarded_this_turn:
            self.player.energy += 2

    def Sucker_Punch(self):
        self.damage(7, 2)
        p.apply("weak", self.target, duration=1+self.upgrades)

    def Accuracy(self):
        # TODO: accuracy power
        p.apply("accuracy", self.target, intensity=3+2*self.upgrades)

    def All_Out_Attack(self):
        self.damage_all(10, 4)
        self.discard()

    def Backstab(self):
        self.damage(11, 4)

    def Blur(self):
        self.block(5,3)
        # TODO: blur power
        p.apply("blur", self.target, duration=1)

    def Bouncing_Flask(self):
        for _ in range(3 + self.upgrades):
            self.poison(3,0)

    def Calculated_Gamble(self):
        n = len(self.hand)
        self.discard(n)
        self.draw(n)

    def Caltrops(self):
        p.apply("thorns", intensity=+self.upgrades*2)

    def Catalyst(self):
        self.poison(self.target.powers['poison'], self.target.powers['poison'])

    def Choke(self):
        self.damage(12, 0)
        p.apply("choke", intensity=3+self.upgrades*2, duration=1)

    def Concentrate(self):
        self.discard(3)
        self.player.energy += 2

    def Crippling_Cloud(self):
        for m in self.monsters:
            self.target = m
            self.poison(4, 3)
            p.apply("weak", self.target, duration=2)

    def Dash(self):
        self.block(10, 3)
        self.damage(10, 3)

    def Distraction(self):
        # TODO
        pass

    def Endless_Agony(self):
        #TODO
        self.damage(4, 2)

    def Escape_Plan(self):
        self.draw(1)
        if (self.hand[len(self.hand) -1]).card_type == CardType.SKILL:
            self.block(3, 2)

    def Eviscerate(self):
        #TODO
        for _ in range(3):
            self.damage(6, 2)

    def Expertise(self):
        if len(self.hand) < 6:
            self.draw(6-len(self.hand))

    def Finisher(self):
        for _ in range(self.attack_count):
            self.damage(6, 2)

    def Footwork(self):
        p.apply("dexterity", self.player, intensity=2+self.upgrades)

    def Heel_Hook(self):
        self.damage(5, 3)
        # TODO: fix this? maybe?
        if self.target.powers["weak"] and self.target.powers["weak"]["duration"] > 0:
            self.player.energy += 1

    def Infinite_Blades(self):
        p.apply("infinite_blades", self.player, intensity=1)

    def Leg_Sweep(self):
        p.apply("weak", self.target, duration=2+self.upgrades)
        self.block(11, 3)

    def Masterful_Stab(self):
        # TODO
        self.damage(12, 4)

    def Noxious_Fumes(self):
        p.apply("noxious_fumes", self.player, intensity=2+self.upgrades)

    def Predator(self):
        self.damage(15, 5)
        p.apply("draw_next", self.player, duration=1, intensity=2)

    def Reflex(self):
        # TODO
        pass

    def Riddle_With_Holes(self):
        for _ in range(5):
            self.damage(3, 1)

    def Setup(self):
        card = random.randint(0, len(self.hand)-1)
        self.hand.pop(card)
        self.draw_pile.append(card)

    def Skewer(self):
        for _ in range(self.player.energy):
            self.damage(7, 3)

    def Tactician(self):
        pass

    def Terror(self):
        p.apply("vulnerable", duration=99)

    #todo: check id
    def Well_Laid_Plans(self):
        p.apply("retain", intensity=1+self.upgrades)

    def A_Thousand_Cuts(self):
        p.apply("thousand_cuts", intensity=1+self.upgrades)

    def Adrenaline(self):
        self.draw(2)
        self.player.energy += 1

    def After_Image(self):
        p.apply("after_image", intensity=1+self.upgrades)

    def Alchemize(self):
        pass

    def Bullet_Time(self):
        p.apply("bullet_time")
        p.apply("no_draw", duration=1)

    def Burst(self):
        p.apply("burst", duration=1, intensity=1+self.upgrades)

    def Corpse_Explosion(self):
        self.poison(6, 3)
        p.apply("corpse_explosion", self.target)

    def Die_Die_Die(self):
        self.damage_all(13, 4)

    def Doppelganger(self):
        p.apply("next_draw", duration=1, intensity=self.player.energy)
        p.apply("next_energy", duration=1, intensity=self.player.energy)

    def Envenom(self):
        p.apply("envenom", intensity=1)

    def Glass_Knife(self):
        # TODO
        for _ in range(2):
            self.damage(8 - 2*self.glass_knife_count, 4)
        self.glass_knife_count += 1

    def Grand_Finale(self):
        # TODO
        pass

    def Malaise(self):
        p.apply("strength", self.target, intensity=-1*self.player.energy)
        p.apply("weak", self.target, duration=self.player.energy)

    def Nightmare(self):
        p.apply("nightmare", random.choice(self.hand))

    def Phantasmal_Killer(self):
        p.apply("double_damage", duration=1)

    def Storm_Of_Steel(self):
        n = len(self.hand)
        self.discard(n)
        for _ in range(n):
            self.get_shiv(self.upgrades)

    def Tools_Of_The_Trade(self):
        # todo
        p.apply("tools_of_the_trade")

    def Unload(self):
        self.damage(14, 4)
        for c in self.hand:
            if c.card_type != CardType.ATTACK:
                self.discard(card=c)

    def Wraith_Form(self):
        p.apply("intangible", duration=2+self.upgrades)
        p.apply("wraith_form", intensity=2)