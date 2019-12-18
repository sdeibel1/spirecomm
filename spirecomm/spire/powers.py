import spirecomm.spire.card


class SimPower:
    """Class for powers and buffs/debuffs, such as weak, vulnerable, strength, poison, etc. for simulation.
    Due to the relatively small number of powers needed to implement to simulate one class in one act, this was
    kept to a single class. However, in the future, this should definitely be refactored to have an overarching power
    class and many classes (one for each power) which extend that power class.
    Author: Sebastian Deibel
    """

    @classmethod
    def set_sim(cls, sim):
        cls.sim = sim

    @classmethod
    def apply(cls, key, target=None, intensity=-1, duration=-1):
        if target is None:
            target = cls.sim.player
        elif isinstance(target, int):
            target = cls.sim.monsters[target]
        if key == "slime":
            for _ in range(intensity):
                cls.sim.discard_pile.append(spirecomm.spire.card.Card("slime", "slime", spirecomm.spire.card.CardType.STATUS,
                                                                      spirecomm.spire.card.CardRarity.BASIC, is_playable=False))
                return

        if target.sim_powers["artifact"] > 0:
            target.sim_powers["artifact"] -= 1
            return

        if key in target.sim_powers:
            # print(key, target, intensity, duration)
            if isinstance(target.sim_powers[key], int):
                target.sim_powers[key] += intensity
                return
            if intensity > -1:
                if "intensity" in target.sim_powers[key]:
                    target.sim_powers[key]["intensity"] += intensity
                else:
                    target.sim_powers[key]["intensity"] = intensity
            if duration > -1:
                if "duration" in target.sim_powers[key]:
                    target.sim_powers[key]["duration"] += duration
                else:
                    target.sim_powers[key]["duration"] = duration

        if key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            target.sim_powers[attr] += intensity

    # do I actually need this?
    # @classmethod
    # def apply_all(cls, key, n=0):
    #     for target in cls.sim.monsters:
    #         if target.sim_powers["artifact"] > 0:
    #             target.sim_powers["artifact"] -= 1
    #         elif target.sim_powers[key]:
    #             target.sim_powers[key] += n
    #         else:
    #             target.sim_powers[key] = n

    @classmethod
    def on_attack_damage(cls, key, power_source, damage_source, damage_target):
        power = power_source.sim_powers[key]
        if key == "thorns":
            cls.sim.damage(power["intensity"], is_attack=False, target=damage_source)
        if key == "envenom":
            cls.sim.poison(1, 0, target=damage_target)


    @classmethod
    def on_card_play(cls, key, source):
        power = source.sim_powers[key]
        if key == "Choke":
            target = power["target"]
            cls.sim.damage(power["intensity"], is_attack=False, target=power["target"])
        if key == "thousand_cuts":
            cls.sim.damage_all(1, power["card"].upgrades)

    @classmethod
    def on_start_turn(cls, key, source):
        power = source.sim_powers[key]
        if key == "poison":
            source.current_hp -= power
            if power >= 1:
                source.sim_powers[key] -= 1
        if key == "dodge_and_roll":
            source.block += power["intensity"]
        if key == "infinity_blades":
            cls.sim.get_shiv()
        if key == "draw_next":
            cls.sim.draw(power["intensity"])
        if key == "energy_next":
            cls.sim.get_player().energy += power["intensity"]
        if key == "noxious_fumes":
            for m in cls.sim.monsters:
                cls.sim.poison(power["intensity"], power["card"].upgrades, m)

    @classmethod
    def end_of_turn(cls, key, source):
        # duration only
        # "double_tap", "flame_barrier", "rebound", "amplify",
        power = source.sim_powers[key]
        if key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            if power["duration"] > 0:
                source.sim_powers[attr]["intensity"] -= source.sim_powers[key]["intensity"]
        if key == "Ritual":
            source.sim_powers["strength"] += power["intensity"]
        
        if type(power) is dict and power["duration"] > 0:
            power["duration"] -= 1
            if power["duration"] == 0:
                source.sim_powers.pop(key)

        # intensity and duration
        if key in {"strength_temp", "dexterity_temp", "focus_temp"}:
            attr = key[:key.index("_")]
            if power["duration"] > 0:
                source.sim_powers[attr]["intensity"] -= source.sim_powers[key]["intensity"]
                source.sim_powers[key]["duration"] -= 1
                power["intensity"] = 0
        else:
            pass

    @classmethod
    def on_death(cls, key, source):
        power = source.sim_powers[key]
        if key == "corpse_explosion":
            for m in cls.sim.monsters:
                cls.sim.damage(power["intensity"], is_attack=False, target=m)
        if hasattr(source, "name") and source.name == "Fungi Beast":
            cls.apply("vulnerable", cls.sim.player, duration=3)
