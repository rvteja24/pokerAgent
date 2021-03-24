from math import floor, ceil


class ActionAbstracter:

    # to be used by the agent while generating trees; need to include pot value into calculating proportionality of raise
    def get_abstracted_raise_values(self, min_val, round,  max_raise, pot_val):
        raise_vals = []
        incr = 0
        if round == "preflop":
            pot_splits = [0.25, 0.5, 0.75, 1.0, 1.25 ,1.5, 1.75, 2.0]
        elif round == "flop":
            pot_splits = [ 0.5, 0.75, 1.0 ,1.5, 1.75, 2.0]
        elif round == "turn":
            pot_splits = [0.5, 1.0, 1.5, 2.0]
        elif round == "river":
            pot_splits = [ 0.5, 1.0, 2.0]

        for each in pot_splits:
            if min_val <= each * pot_val < max_raise:
                raise_vals.append(each)
        if max_raise/pot_val not in raise_vals and max_raise > 0:
            raise_vals.append("allin")
        return raise_vals

    # to be used for mapping opponent moves during search
    def get_mappable_raise_value(self, raise_value):
        return floor(raise_value/100) * 100

