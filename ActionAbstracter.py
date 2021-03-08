from math import floor


class ActionAbstracter:
    # to be used by the agent while generating trees
    def get_abstracted_raise_values(self, stack):
        raise_vals = []
        rounded_stack = floor(stack / 100) * 100
        print(rounded_stack)
        while rounded_stack != 0:
            raise_vals.append(rounded_stack)
            rounded_stack -= 100
        return raise_vals

    # to be used for mapping opponent moves during search
    def get_mappable_raise_value(self, raise_value):
        return floor(raise_value/100) * 100
