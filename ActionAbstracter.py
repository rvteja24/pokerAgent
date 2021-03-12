from math import floor

class ActionAbstracter:
    # to be used by the agent while generating trees; need to include pot value into calculating proportionality of raise
    def get_abstracted_raise_values(self, stack, pot_value, min_raise):
        raise_vals = []
        rounded_stack = floor(stack / 100) * 100
        print(rounded_stack)
        while rounded_stack != min_raise:
            raise_vals.append(rounded_stack)
            rounded_stack -= 100
        return raise_vals

    # to be used for mapping opponent moves during search
    def get_mappable_raise_value(self, raise_value):
        return floor(raise_value/100) * 100

