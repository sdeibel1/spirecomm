from spirecomm.ai.combatSim import CombatSim


class SimPower:

    @classmethod
    def apply(cls, key, target=CombatSim.player, intensity=-1, duration=-1):
        if target.powers["artifact"] > 0:
            target.powers["artifact"] -= 1
        elif target.powers[key]:
            if intensity > -1:
                target.powers[key]["intensity"] += intensity
            if duration > -1:
                target.powers[key]["duration"] += duration
        else:
            target.powers[key]["intensity"] = intensity
            target.powers[key]["duration"] = duration

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
        if key in {"weak", "vulnerable", "frail", "choke", "no_draw", "no_block", "entangled", "burst", "amplify", "double_damage",
                   "double_tap", "flame_barrier", "rebound", }:
            source.powers[key]['duration'] -= 1
        # intensity and duration
        elif key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            source.powers[attr]["intensity"] -= source.powers[key]["intensity"]
            source.powers[key]["duration"] -= 1
        else:
            pass