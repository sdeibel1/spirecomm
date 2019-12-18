import copy
import random

import spirecomm.spire.card
import spirecomm.spire.move_info
import spirecomm.spire.relic
import spirecomm.spire.character
import spirecomm.spire.potion
import spirecomm.spire.powers


# noinspection PyPep8Naming
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

        spirecomm.spire.powers.SimPower.set_sim(self)

    @classmethod
    def from_json(cls, game_state):
        combat_state = game_state['combat_state']
        state = {'player': spirecomm.spire.character.Player.from_json(game_state),
                 'deck': [spirecomm.spire.card.Card.from_json(c) for c in game_state['deck']],
                 'relics': [spirecomm.spire.relic.Relic.from_json(r) for r in game_state['relics']],
                 'potions': [spirecomm.spire.potion.Potion.from_json(p) for p in game_state['potions']],
                 'hand': [spirecomm.spire.card.Card.from_json(c) for c in combat_state['hand']],
                 'draw_pile': [spirecomm.spire.card.Card.from_json(c) for c in combat_state['draw_pile']],
                 'discard_pile': [],
                 'exhaust_pile': [],
                 'monsters': [spirecomm.spire.character.Monster.from_json(m) for m in combat_state['monsters']],
                 'turn': 0}
        sim = CombatSim(state)
        return sim

    def get_state(self):
        # player = Player(self.player.max_hp, self.hand[:], self.player.current_hp, self.player.block, self.player.energy)
        return copy.deepcopy({'player': self.player,
                'deck': self.deck,
                'relics': self.relics,
                'potions': self.potions,
                'hand': self.hand,
                'draw_pile': self.draw_pile,
                'discard_pile': self.discard_pile,
                'exhaust_pile': self.exhaust_pile,
                'monsters': self.monsters,
                'turn': self.turn})

    def change_state(self, state):
        x = 2
        newstate = copy.deepcopy(state)
        self.player = newstate['player']
        self.deck = newstate['deck']
        self.relics = newstate['relics']
        self.potions = newstate['potions']
        self.hand = newstate['hand']
        self.draw_pile = newstate['draw_pile']
        self.discard_pile = newstate['discard_pile']
        self.exhaust_pile = newstate['exhaust_pile']
        self.monsters = newstate['monsters']
        self.turn = newstate['turn']



        # self.player = copy.deepcopy(state['player'])
        # self.deck = state['deck'][:]
        # self.relics = state['relics'][:]
        # self.potions = state['potions'][:]
        # self.hand = state['hand'][:]
        # self.draw_pile = state['draw_pile'][:]
        # self.discard_pile = state['discard_pile'][:]
        # self.exhaust_pile = state['exhaust_pile'][:]
        # self.monsters = [copy.deepcopy(m) for m in state['monsters']]
        # self.turn = state['turn']


    def step_one_turn(self):
        self.on_start_turn()
        self.do_player_action()
        self.end_player_turn()
        self.do_monster_actions()
        self.end_monster_turn()
        self.turn += 1

    def finish_turn(self):
        available = [c for c in self.hand if self.player.can_play(c)]
        while any([self.player.can_play(c) for c in available]):
            card_to_play = random.randint(0, len(available)-1)
            target = random.randint(0, len(self.monsters) - 1) if available[card_to_play].has_target else -1
            self.play(available[card_to_play], target)
            available.pop(card_to_play)
        self.end_player_turn()
        self.do_monster_actions()
        self.end_monster_turn()
        self.turn += 1

    def on_start_turn(self):
        self.draw(5)
        self.player.energy = 3
        # for r in self.relics:
        #     r.on_start_turn()  # TODO: implement
        self.player.on_start_turn()
        for m in self.monsters:
            m.on_start_turn()

    def do_player_action(self):
        if self.player.affected_by("entangled"):
            return
        available_cards = [c for c in self.hand if self.player.can_play(c)]
        if available_cards:
            card_to_play = random.choice(available_cards)
            alive = [i for i, m in enumerate(self.monsters) if not m.is_gone]
            target = random.choice(alive) if card_to_play.has_target else -1
            # print("card: {0}, target: {1}, player block: {2}".format(card_to_play.name, target, self.player.block))
            self.play(card_to_play, target)
        # mcts = MCTS(self, self.get_state())
        # card, target = mcts.get_action()
        # self.play(card, target)

    def do_monster_actions(self):
        alive = [monster for monster in self.monsters if monster.current_hp > 0]
        for monster in alive:
            if self.turn >= len(monster.move_info.schedule):
                possible_moves = monster.move_info.schedule[-1]  # tuple
            else:
                possible_moves = monster.move_info.schedule[self.turn]  # tuple

            if isinstance(possible_moves[0], spirecomm.spire.move_info.Move):
                # random selection
                move = random.choices(possible_moves, weights=[x.prob for x in possible_moves])[0]
            elif possible_moves[0] == "alternate":
                # possible_moves[1] is a tuple with the two moves to alternate
                if possible_moves[1][0].name == monster.get_move_name_by_id(monster.last_move_id):
                    move = possible_moves[1][1]
                else:
                    move = possible_moves[1][0]
            # print("move: {0}, move damage: {1}, monster block: {2}".format(move.name, move.damage, monster.block))
            self.do_monster_move(move, monster)

    def do_monster_move(self, move, monster):
        if move.intent in {spirecomm.spire.move_info.Intent.SLEEP, spirecomm.spire.move_info.Intent.STUN, spirecomm.spire.move_info.Intent.NONE}:
            return
        if move.intent is spirecomm.spire.move_info.Intent.UNKNOWN:
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
            spirecomm.spire.powers.SimPower.apply(move.buff_name, monster, move.intensity, move.duration)
        if move.debuff_name:
            spirecomm.spire.powers.SimPower.apply(move.debuff_name,intensity=move.intensity, duration=move.duration)

    def end_player_turn(self):
        self.player.on_end_turn()
        for m in self.monsters:
            m.block = 0
        self.discard(len(self.hand))

    def end_monster_turn(self):
        for m in self.monsters:
            m.on_end_turn()
        self.player.block = 0

    def sim_combat(self, card, target):
        # print("AAAAAAAAAAAAAAAAAAH", card.name, target)
        with open("log.txt", "w") as f:
            f.write(str(card.name) + " " + str(target))
        self.play(card, target)
        self.finish_turn()
        while self.player.current_hp >= 0 and any(m.current_hp >= 0 for m in self.monsters):
            self.step_one_turn()
            # print("player hp:", self.player.current_hp)
            # for i, m in enumerate(self.monsters):
                # print("monster {0} hp, {1}".format(i, m.current_hp))
        return 0 if self.player.current_hp <= 0 else 1


    def is_over(self):
        if self.player.current_hp <= 0 or all(m.current_hp <= 0 for m in self.monsters):
            return True
        return False

    def play(self, card, target):
        if target == -1:
            target = self.player
        else:
            target = self.monsters[target]
        self.target = target
        self.cost = card.cost
        self.upgrades = card.upgrades
        card_method = card.card_id.replace(" ", "_")
        getattr(CombatSim, card_method)(self)
        self.player.on_card_play()
        self.player.energy -= self.cost

    def draw(self, n):
        if n == 0:
            return
        if len(self.draw_pile) == 0:
            if len(self.discard_pile) == 0:
                return
            self.draw_pile.extend(self.discard_pile)
            random.shuffle(self.draw_pile)
            self.discard_pile.clear()

        if len(self.hand) == 10:
            self.discard_pile.append(self.draw_pile.pop())
        else:
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
        amt = base + self.upgrades * add + source.sim_powers['strength']
        if "weak" in source.sim_powers:
            amt *= .75
        if "vulnerable" in target.sim_powers:
            amt *= 1.5
        after_block = amt - target.block
        target.block = max(target.block - amt, 0)
        target.current_hp -= max(after_block, 0)
        if is_attack is True:
            for power in source.sim_powers:
                spirecomm.spire.powers.SimPower.on_attack_damage(power, source, source, target)
            for power in target.sim_powers:
                spirecomm.spire.powers.SimPower.on_attack_damage(power, target, source, target)
        if target.current_hp <= 0:
            for power in source.sim_powers:
                spirecomm.spire.powers.SimPower.on_death(power, source)
            for power in target.sim_powers:
                spirecomm.spire.powers.SimPower.on_death(power, target)
        # source.onReceiveDamage
        # target.onDealDamage (?)

    def damage_all(self, base, add, is_attack=True):
        source = self.player
        temp_amt = base + source.sim_powers['strength']
        if source.affected_by("weak"):
            temp_amt *= .75
        for target in self.monsters:
            amt = temp_amt
            # TODO: adjust damage for buffs/debuffs (strength, weakness, vuln, etc.)
            if target.affected_by('vulnerable'):
                amt *= 1.5
            after_block = amt - target.block
            target.block = max(target.block - amt, 0)
            target.current_hp -= max(after_block, 0)
            if is_attack is True:
                for power in source.sim_powers:
                    spirecomm.spire.powers.SimPower.on_attack_damage(power, source, source, target)
                for power in target.sim_powers:
                    spirecomm.spire.powers.SimPower.on_attack_damage(power, target, source, target)

    def block(self, base, add=0, target=None):
        if target is None:
            target = self.player
        amt = base + self.upgrades * add + target.sim_powers['dexterity']
        if target.affected_by("frail"):
            amt *= .75
        target.block += amt

    def discard(self, n=1, index=-1):
        """
        Discard a card in target (player)'s hand.
        index: if -1, random card, else the card at location index
        """
        if len(self.hand) == 0:
            return
        if n >= len(self.hand):
            self.discard_count += len(self.hand)
            self.discard_pile.extend(self.hand)
            self.hand = []
        elif n > 1:
            for _ in range(n):
                self.discard_pile.append(self.hand.pop())
            self.discard_count += n
        else:
            if index >= 0:
                self.discard_pile.append(self.hand.pop(index))
            else:
                self.discard_pile.append(self.hand.pop())
            self.discard_count += 1

    def get_shiv(self, upgrades=0):
        shiv = spirecomm.spire.card.Card("Shiv", "Shiv", spirecomm.spire.card.CardType.ATTACK, 
                                         spirecomm.spire.card.CardRarity.BASIC, upgrades=upgrades, is_playable=True, exhausts=True)
        self.hand.append(shiv)

    def poison(self, base, add, target=None):
        if target is None:
            target = self.target
        target.sim_powers['poison'] += (base + self.upgrades * add)

    # CARDS
    def Strike_G(self):
        self.damage(6, 3)

    def Defend_G(self):
        self.block(6, 3)

    def Neutralize(self):
        self.damage(4, 2)
        spirecomm.spire.powers.SimPower.apply("weak", target=self.target, duration=1+self.upgrades)

    def Survivor(self):
        self.block(8, 3)
        self.discard()

    def Acrobatics(self):
        self.draw(3)
        self.discard()  # self.target is the chosen card to discard here

    def Backflip(self):
        self.block(5,3)
        self.draw(2)

    def Bane(self):
        self.damage(7, 3)
        if self.target.sim_powers['poison'] > 0:
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
        self.discard()

    def Deadly_Poison(self):
        self.poison(5, 2)

    def Deflect(self):
        self.block(4, 3)

    def Dodge_and_Roll(self):
        self.block(4, 2)
        spirecomm.spire.powers.SimPower.apply("dodge_and_roll", duration=1, intensity=4+2*self.upgrades)

    def Flying_Knee(self):
        self.damage(8, 3)
        spirecomm.spire.powers.SimPower.apply("next_energy", duration=1, intensity=1)

    def Outmaneuver(self):
        # TODO: next_energy power
        spirecomm.spire.powers.SimPower.apply("next_energy", duration=1, intensity=2)

    def PiercingWail(self):
        # TODO: apply all???
        for t in self.monsters:
            spirecomm.spire.powers.SimPower.apply("strength_temp", target=t, intensity=-(6+2*self.upgrades))

    def Poisoned_Stab(self):
        self.damage(6, 2)
        self.poison(3, 1)

    def Prepared(self):
        self.draw(1+self.upgrades)
        self.discard(n=1+self.upgrades)

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
        spirecomm.spire.powers.SimPower.apply("weak", target=self.target, duration=1+self.upgrades)

    def Accuracy(self):
        # TODO: accuracy power
        spirecomm.spire.powers.SimPower.apply("accuracy", intensity=3+2*self.upgrades)

    def All_Out_Attack(self):
        self.damage_all(10, 4)
        self.discard()

    def Backstab(self):
        self.damage(11, 4)

    def Blur(self):
        self.block(5,3)
        # TODO: blur power
        spirecomm.spire.powers.SimPower.apply("blur", self.target, duration=1)

    def Bouncing_Flask(self):
        for _ in range(3 + self.upgrades):
            self.poison(3, 0)

    def Calculated_Gamble(self):
        n = len(self.hand)
        self.discard(n=n)
        self.draw(n)

    def Caltrops(self):
        spirecomm.spire.powers.SimPower.apply("thorns", intensity=+self.upgrades*2)

    def Catalyst(self):
        self.poison(self.target.sim_powers['poison'], self.target.sim_powers['poison'])

    def Choke(self):
        self.damage(12, 0)
        spirecomm.spire.powers.SimPower.apply("choke", target=self.target, intensity=3+self.upgrades*2, duration=1)

    def Concentrate(self):
        self.discard(n=3)
        self.player.energy += 2

    def Crippling_Poison(self):
        for m in self.monsters:
            self.target = m
            self.poison(4, 3)
            spirecomm.spire.powers.SimPower.apply("weak", target=m, duration=2)

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
        if (self.hand[len(self.hand) -1]).type == spirecomm.spire.card.CardType.SKILL:
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
        spirecomm.spire.powers.SimPower.apply("dexterity", self.player, intensity=2+self.upgrades)

    def Heel_Hook(self):
        self.damage(5, 3)
        # TODO: fix this? maybe?
        if self.target.sim_powers["weak"] and self.target.sim_powers["weak"]["duration"] > 0:
            self.player.energy += 1

    def Infinite_Blades(self):
        spirecomm.spire.powers.SimPower.apply("infinite_blades", self.player, intensity=1)

    def Leg_Sweep(self):
        spirecomm.spire.powers.SimPower.apply("weak", target=self.target, duration=2+self.upgrades)
        self.block(11, 3)

    def Masterful_Stab(self):
        # TODO
        self.damage(12, 4)

    def Noxious_Fumes(self):
        spirecomm.spire.powers.SimPower.apply("noxious_fumes", self.player, intensity=2+self.upgrades)

    def Predator(self):
        self.damage(15, 5)
        spirecomm.spire.powers.SimPower.apply("draw_next", self.player, duration=1, intensity=2)

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
        spirecomm.spire.powers.SimPower.apply("vulnerable", target=self.target, duration=99)

    def Well_Laid_Plans(self):
        spirecomm.spire.powers.SimPower.apply("retain", intensity=1+self.upgrades)

    def A_Thousand_Cuts(self):
        spirecomm.spire.powers.SimPower.apply("thousand_cuts", intensity=1+self.upgrades)

    def Adrenaline(self):
        self.draw(2)
        self.player.energy += 1

    def After_Image(self):
        spirecomm.spire.powers.SimPower.apply("after_image", intensity=1+self.upgrades)

    def Alchemize(self):
        pass

    def Bullet_Time(self):
        # TODO
        spirecomm.spire.powers.SimPower.apply("bullet_time")
        # TODO
        spirecomm.spire.powers.SimPower.apply("no_draw", duration=1)

    def Burst(self):
        spirecomm.spire.powers.SimPower.apply("burst", duration=1, intensity=1+self.upgrades)

    def Corpse_Explosion(self):
        self.poison(6, 3)
        spirecomm.spire.powers.SimPower.apply("corpse_explosion", target=self.target)

    def Die_Die_Die(self):
        self.damage_all(13, 4)

    def Doppelganger(self):
        spirecomm.spire.powers.SimPower.apply("next_draw", duration=1, intensity=self.player.energy)
        spirecomm.spire.powers.SimPower.apply("next_energy", duration=1, intensity=self.player.energy)

    def Envenom(self):
        spirecomm.spire.powers.SimPower.apply("envenom", intensity=1)

    def Glass_Knife(self):
        # TODO
        for _ in range(2):
            self.damage(8 - 2*self.glass_knife_count, 4)
        self.glass_knife_count += 1

    def Grand_Finale(self):
        # TODO
        pass

    def Malaise(self):
        spirecomm.spire.powers.SimPower.apply("strength", target=self.target, intensity=-1*self.player.energy)
        spirecomm.spire.powers.SimPower.apply("weak", target=self.target, duration=self.player.energy)

    def Nightmare(self):
        spirecomm.spire.powers.SimPower.apply("nightmare", random.choice(self.hand))

    def Phantasmal_Killer(self):
        spirecomm.spire.powers.SimPower.apply("double_damage", duration=1)

    def Storm_Of_Steel(self):
        n = len(self.hand)
        self.discard(n=n)
        for _ in range(n):
            self.get_shiv(self.upgrades)

    def Tools_Of_The_Trade(self):
        # todo
        spirecomm.spire.powers.SimPower.apply("tools_of_the_trade")

    def Unload(self):
        self.damage(14, 4)
        to_discard = []
        for i, c in enumerate(self.hand):
            if c.card_type != spirecomm.spire.card.CardType.ATTACK:
                to_discard.append(i)
        for i in to_discard:
            self.discard(index=i)

    def Wraith_Form(self):
        spirecomm.spire.powers.SimPower.apply("intangible", duration=2+self.upgrades)
        spirecomm.spire.powers.SimPower.apply("wraith_form", intensity=2)

    def Slimed(self):
        pass

    def Shiv(self):
        self.damage(4,2)
