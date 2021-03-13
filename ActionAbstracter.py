from math import floor

class ActionAbstracter:
    # to be used by the agent while generating trees; need to include pot value into calculating proportionality of raise
    def get_abstracted_raise_values(self, min_val, pot_val, max_raise):
        raise_vals = []
        pot_proportions = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5]
        for each in pot_proportions:
            if max_raise >= each * pot_val >= min_val:
                raise_vals.append(each * pot_val)
        if max_raise > 0:
            raise_vals.append(max_raise)
        return raise_vals

    # to be used for mapping opponent moves during search
    def get_mappable_raise_value(self, raise_value):
        return floor(raise_value/100) * 100

