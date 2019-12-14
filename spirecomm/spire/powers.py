from spirecomm.ai.combatSim import CombatSim
from spirecomm.spire.card import CardType, Card, CardRarity


class SimPower:

    @classmethod
    def apply(cls, key, target=CombatSim.player, intensity=-1, duration=-1):
        if key == "slime":
            for _ in range(intensity):
                CombatSim.discard_pile.append(Card("slime", "slime", CardType.STATUS, CardRarity.BASIC, is_playable=False))
                return

        if target.powers["artifact"] > 0:
            target.powers["artifact"] -= 1
            return

        if target.powers[key]:
            if intensity > -1:
                target.powers[key]["intensity"] += intensity
            if duration > -1:
                target.powers[key]["duration"] += duration
        else:
            target.powers[key]["intensity"] = intensity
            target.powers[key]["duration"] = duration

        if key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            target.powers[attr] += intensity

    # do I actually need this?
    @classmethod
    def apply_all(cls, key, n=0):
        for target in CombatSim.monsters:
            if target.powers["artifact"] > 0:
                target.powers["artifact"] -= 1
            elif target.powers[key]:
                target.powers[key] += n
            else:
                target.powers[key] = n

    @classmethod
    def end_of_turn(cls, key, source):
        # duration only
        # "double_tap", "flame_barrier", "rebound", "amplify",
        power = source.powers[key]
        if key in {"weak", "vulnerable", "frail", "choke", "no_draw", "no_block", "entangled", "burst", "double_damage"}:
            if power['duration'] > 0:
                power['duration'] -= 1
        # intensity and duration
        elif key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            if power["duration"] > 0:
                source.powers[attr]["intensity"] -= source.powers[key]["intensity"]
                source.powers[key]["duration"] -= 1
                power["intensity"] = 0
        else:
            pass