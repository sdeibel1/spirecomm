from enum import Enum
import random


class Intent(Enum):
    ATTACK = 1
    ATTACK_BUFF = 2
    ATTACK_DEBUFF = 3
    ATTACK_DEFEND = 4
    BUFF = 5
    DEBUFF = 6
    STRONG_DEBUFF = 7
    DEBUG = 8
    DEFEND = 9
    DEFEND_DEBUFF = 10
    DEFEND_BUFF = 11
    ESCAPE = 12
    MAGIC = 13
    NONE = 14
    SLEEP = 15
    STUN = 16
    UNKNOWN = 17

    def is_attack(self):
        return self in [Intent.ATTACK, Intent.ATTACK_BUFF, Intent.ATTACK_DEBUFF, Intent.ATTACK_DEFEND]


class MoveInfo:
    MOVE_IDS = {
        "Cultist": {"Incantation": 3, "Dark Strike": 1},
        "Jaw Worm": {"Chomp": 1, "Bellow": 2, "Thrash": 3},
        "Acid Slime (S)": {"Tackle": 1, "Lick": 2},
        "Acid Slime (M)": {"Corrosive Spit": 1, "Tackle": 2, "Lick": 4},
        "Acid Slime (L)": {"Corrosive Spit": 1, "Tackle": 2, "Split": 3, "Lick": 4},
        "Spike Slime (S)": {"Tackle": 1},
        "Spike Slime (M)": {"Flame Tackle": 1, "Lick": 4},
        "Spike Slime (L)": {"Flame Tackle": 1, "Split": 3, "Lick": 4},
        "Green Louse": {"Bite": 3, "Spit Web": 4},
        "Red Louse": {"Bite": 3, "Grow": 4}
    }

    def __init__(self, monster):
        self.monster = monster
        self.schedule = []
        self.get_info(monster)

    def get_info(self, monster):
        n = monster.name
        if n == "Cultist":
            incantation = Move("Incantation", Intent.BUFF, buff_name="Ritual", intensity=3)
            dark_strike = Move("Dark Strike", Intent.ATTACK, damage=6)
            self.schedule = [(incantation,), (dark_strike,)]
        elif n == "Jaw Worm":
            chomp = Move("Chomp", Intent.ATTACK, damage=11, prob=.25)
            thrash = Move("Thrash", Intent.ATTACK_DEFEND, damage=7, block=5, prob=.30)
            bellow = Move("Bellow", Intent.DEFEND_BUFF, block=6, buff_name="strength", intensity=3, prob=.45)
            self.schedule = [(chomp,), (chomp, thrash, bellow)]
        elif "Acid Slime" in n:
            lick = Move("Lick", Intent.DEBUFF, debuff_name="weak", duration=1, prob=.5)
            tackle = Move("Tackle", Intent.ATTACK, damage=3, prob=.5)
            corrosive_spit = Move("Corrosive Spit", Intent.ATTACK_DEBUFF, damage=7, debuff_name="slime",
                                  intensity=1, limit=2, prob=.3)
            if "(S)" in n:
                self.schedule = [(lick, tackle), ("alternate", (lick, tackle))]
            else:
                lick.limit, lick.prob = 1, .3
                tackle.limit, tackle.prob = 2, .4
                if "(M)" in n:
                    lick.duration = 1
                    tackle.damage = 10
                if "(L)" in n:
                    lick.duration = 2
                    tackle.damage = 16
                    corrosive_spit.damage, corrosive_spit.intensity = 11, 2
                self.schedule = [(lick, tackle, corrosive_spit)]
        elif "Spike Slime" in n:
            flame_tackle = Move("Flame Tackle", Intent.ATTACK_DEBUFF, debuff_name="slime", limit=2)
            lick = Move("Lick", Intent.DEBUFF, debuff_name="frail", limit=2)
            if "(S)" in n:
                tackle = Move("Tackle", Intent.ATTACK, damage=5)
                self.schedule = [(tackle,)]
            else:
                if "(M)" in n:
                    flame_tackle.damage, flame_tackle.intensity = 8, 1
                    lick.duration = 1
                else:
                    flame_tackle.damage, flame_tackle.intensity = 16, 2
                    lick.duration = 2
                self.schedule = [(flame_tackle, lick)]
        elif "Louse" in n:
            d1 = random.randint(5, 7)
            d2 = random.randint(5, 7)
            bite = Move("Bite", Intent.ATTACK, limit=2, prob=.75)
            if "Green" in n:
                bite.damage = d1
                spit_web = Move("Spit Web", Intent.DEBUFF, debuff_name="weak", duration=2, limit=2, prob=.25)
                self.schedule = [(bite, spit_web)]
            else:
                bite.damage = d2
                grow = Move("Grow", Intent.BUFF, buff_name="strength", intensity=3, limit=2, prob=.25)
                self.schedule = [(bite, grow)]
        elif "Slaver" in n:
            stab = Move("Stab", Intent.ATTACK, limit=2)
            if "Blue" in n:
                stab.prob = .60
                stab.damage = 12
                rake = Move("Rake", Intent.ATTACK_DEBUFF, damage=7, debuff_name="weak", duration=1, prob=.40)
                self.schedule = [(stab, rake)]
            else:
                stab.prob = .45
                stab.damage = 13
                scrape = Move("Scrape", Intent.ATTACK_DEBUFF, damage=8, debuff_name="vulnerable", duration=1, prob=.55)
                entangle = Move("Entangle", Intent.DEBUFF, debuff_name="entangled", duration=1)
                self.schedule = [(stab,), (scrape,), (entangle,), (stab, scrape)]
        elif n == "Fungi Beast":
            bite = Move("Bite", Intent.ATTACK, damage=6, limit=2, prob=.60)
            grow = Move("Grow", Intent.BUFF, buff_name="strength", intensity=3, limit=1, prob=.40)

        else:
            pass
        

class Move:

    def __init__(self, name, intent, damage=0, multi=1, block=0, buff_name="", debuff_name="",
                 intensity=-1, duration=-1, limit=None, prob=1):
        self.name = name
        self.intent = intent
        self.damage = damage
        self.multi = multi
        self.block = block
        self.buff_name = buff_name
        self.debuff_name = debuff_name
        self.intensity = intensity
        self.duration = duration
        self.limit = limit
        self.prob = prob


