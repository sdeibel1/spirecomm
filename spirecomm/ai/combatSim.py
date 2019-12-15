import random

from spirecomm.ai.mcts import MCTS
from spirecomm.spire.card import Card, CardType, CardRarity
from spirecomm.spire.move_info import Move
from spirecomm.spire.relic import Relic
from spirecomm.spire.character import Monster, Intent
from spirecomm.spire.character import Player
from spirecomm.spire.potion import Potion
from spirecomm.spire.powers import SimPower as p


class CombatSim:

    def __init__(self, state):
        self.player = state['player']
        self.deck = state['deck']
        self.relics = state['relics']
        self.potions = state['potions']
        self.hand = state['hand']
        self.draw_pile = state['draw_pile']
        self.discard_pile = state['discard_pile']
        self.exhaust_pile = state['exhaust_pile']
        self.monsters = state['monsters']
        self.turn = state['turn']

        # combat_state = game_state['combat_state']
        # self.player = Player.from_json(game_state)
        # self.deck = [Card.from_json(c) for c in game_state['deck']]
        # self.relics = [Relic.from_json(r) for r in game_state['relics']]
        # self.potions = [Potion.from_json(p) for p in game_state['potions']]
        # self.hand = [Card.from_json(c) for c in combat_state['hand']]
        # self.draw_pile = [Card.from_json(c) for c in combat_state['draw_pile']]
        # self.discard_pile = []
        # self.exhaust_pile = []
        # self.monsters = [Monster.from_json(m) for m in combat_state['monsters']]

        # for card playing
        self.target = None
        self.upgrades = 0
        self.cost = 0
        self.discard_count = 0
        self.attack_count = 0
        self.glass_knife_count = 0

    @classmethod
    def from_json(cls, game_state):
        combat_state = game_state['combat_state']
        state = {'player': Player.from_json(game_state),
                 'deck': [Card.from_json(c) for c in game_state['deck']],
                 'relics': [Relic.from_json(r) for r in game_state['relics']],
                 'potions': [Potion.from_json(p) for p in game_state['potions']],
                 'hand': [Card.from_json(c) for c in combat_state['hand']],
                 'draw_pile': [Card.from_json(c) for c in combat_state['draw_pile']],
                 'discard_pile': [],
                 'exhaust_pile': [],
                 'monsters': [Monster.from_json(m) for m in combat_state['monsters']],
                 'turn': 0}
        return CombatSim(state)

    def get_state(self):
        return {'player': self.player,
                'deck': self.deck,
                'relics': self.relics,
                'potions': self.potions,
                'hand': self.hand,
                'draw_pile': self.draw_pile,
                'discard_pile': self.discard_pile,
                'monsters': self.monsters,
                'turn': self.turn}

    def change_state(self, state):
        self.player = state['player']
        self.deck = state['deck']
        self.relics = state['relics']
        self.potions = state['potions']
        self.hand = state['hand']
        self.draw_pile = state['draw_pile']
        self.discard_pile = state['discard_pile']
        self.exhaust_pile = state['exhaust_pile']
        self.monsters = state['monsters']
        self.turn = state['turn']

    def step_one_turn(self):
        print(self.get_state())
        self.on_start_turn()
        self.do_player_action()
        self.end_player_turn()
        self.do_monster_actions()
        self.end_monster_turn()
        self.turn += 1

    def on_start_turn(self):
        self.draw(5)
        # for r in self.relics:
        #     r.on_start_turn()  # TODO: implement
        self.player.on_start_turn()
        for m in self.monsters:
            m.on_start_turn()

    def do_player_action(self):
        available_cards = [c for c in self.hand if self.player.can_play(c)]
        card_to_play = random.choice(available_cards)
        target = random.choice(self.monsters) if card_to_play.has_target else None
        self.play(card_to_play, self.player)
        # mcts = MCTS(self, self.get_state())
        # card, target = mcts.get_action()
        # self.play(card, target)

    def play_with_random_target(self, card):
        if card.has_target:
            target = self.monsters.choice()
            self.play(card, target)

    def do_monster_actions(self):
        hit_limit = True
        for m in self.monsters:
            if self.turn >= len(m.move_info.schedule):
                possible_moves = m.move_info.schedule[-1]
                if isinstance(possible_moves[0], Move):
                    move = random.choices(possible_moves[0], weights=[x.prob for x in possible_moves[0]])
                self.do_monster_move(m.move_info.schedule[-1], m)
            else:
                self.do_monster_move(m.move_info.schedule[self.turn], m)

    def do_monster_move(self, move, monster):
        if move.intent in {Intent.SLEEP, Intent.STUN, Intent.NONE}:
            return
        if move.intent is Intent.UNKNOWN:
            after_split = monster.split()
            self.monsters.pop(monster)
            self.monsters.append(after_split)
            return
        if move.intent.is_attack():
            self.damage(move.damage, source=monster, target=self.player)
        if monster.name == "Shield Gremlin":
            self.block(move.block, target=self.monsters.choice())
        else:
            self.block(move.block, target=monster)
        if move.buff_name:
            p.apply(move.buff_name, monster, move.intensity, move.duration)
        if move.debuff_name:
            p.apply(move.debuff_name,intensity=move.intensity, duration=move.duration)

    def end_player_turn(self):
        self.player.on_end_turn()

    def end_monster_turn(self):
        for m in self.monsters:
            m.on_end_turn()

    def sim_combat(self, card, target):
        self.play(card, target)
        while self.player.current_hp >= 0 and any(m.current_hp >= 0 for m in self.monsters):
            self.step_one_turn()
        if self.player.current_hp <= 0:
            return 0
        else:
            return 1

    def is_over(self):
        if self.player.current_hp <= 0 or all(m.current_hp <= 0 for m in self.monsters):
            return True
        return False

    def play(self, card, target):
        self.target = target
        self.cost = card.cost
        self.upgrades = card.upgrades
        card_method = card.card_id.replace(" ", "_")
        getattr(CombatSim, card_method)(self)
        self.player.on_card_play()

    def draw(self, n):
        if n == 0:
            pass
        elif len(self.hand) == 10:
            self.draw_pile.pop()
        else:
            if len(self.draw_pile) < n:
                self.draw_pile = self.draw_pile.append(self.discard_pile)
                random.shuffle(self.draw_pile)
            self.hand.append(self.draw_pile.pop())
            self.draw(n-1)

    def damage(self, base, add=0, is_attack=True, source=None, target=None):
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
        if target is None:
            target = self.target
        amt = base + self.upgrades * add + source.powers['strength']
        if "weak" in source.powers:
            amt *= .75
        if "vulnerable" in target.powers:
            amt *= 1.5
        after_block = amt - target.block
        target.block = max(target.block - amt, 0)
        target.current_hp -= after_block
        if is_attack is True:
            for power in source.powers:
                p.on_attack_damage(power, source, source, target)
            for power in target.powers:
                p.on_attack_damage(power, target, source, target)
        # source.onReceiveDamage
        # target.onDealDamage (?)

    def damage_all(self, base, add):
        source = self.player
        amt = base + source.powers['strength']
        if source.powers['weak']:
            amt *= .75
        for t in self.target:
            # TODO: adjust damage for buffs/debuffs (strength, weakness, vuln, etc.)
            if self.target.powers['vulnerable']:
                amt *= 1.5
            self.target.current_hp -= amt + self.upgrades * add - self.target.block

    def block(self, base, add=0, target=None):
        if target is None:
            target = self.player
        amt = base + self.upgrades * add + target.powers['dexterity']
        if target.affected_by("frail"):
            amt *= .75
        target.block += amt

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

    def get_shiv(self, upgrades=0):
        shiv = Card("Shiv", "Shiv", CardType.ATTACK, CardRarity.BASIC, upgrades=upgrades, is_playable=True, exhausts=True)
        self.hand.append(shiv)

    def poison(self, base, add, target=None):
        if target is None:
            target = self.target
        target.powers['poison'] += (base + self.upgrades * add)

    # CARDS
    def Strike_G(self):
        self.damage(6, 3)

    def Defend_G(self):
        self.block(6, 3)

    def Neutralize(self):
        self.damage(4, 2)
        p.apply("weak", target=self.target, duration=1+self.upgrades)

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
        self.damage(7, 3)
        if self.target.powers['poison'] > 0:
            self.damage(7, 3)

    def Blade_Dance(self):
        for _ in range(2):
            self.get_shiv()

    def Cloak_And_Dagger(self):
        self.block(6, 0)
        for _ in range(self.upgrades + 1):
            self.get_shiv()

    def Dagger_Spray(self):
        for _ in range(2):
            self.damage_all(4, 2)

    def Dagger_Throw(self):
        self.damage(9, 3)
        self.draw(1)
        self.discard(1)

    def Deadly_Poison(self):
        self.poison(5, 2)

    def Deflect(self):
        self.block(4, 3)

    def Dodge_And_Roll(self):
        self.block(4, 2)
        p.apply("dodge_and_roll", duration=1, intensity=4+2*self.upgrades)

    def Flying_Knee(self):
        self.damage(8, 3)
        p.apply("next_energy", duration=1, intensity=1)

    def Outmaneuver(self):
        # TODO: next_energy power
        p.apply("next_energy", duration=1, intensity=2)

    def Piercing_Wail(self):
        # TODO: apply all???
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
            self.poison(3, 0)

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
        # TODO
        p.apply("bullet_time")
        # TODO
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