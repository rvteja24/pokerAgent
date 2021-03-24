# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:38:04 2021

@author: vijaya_rayavarapu
"""

from pypokerengine.players import BasePokerPlayer
from ActionAbstracter import ActionAbstracter
import random

class BasicPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    def __init__(self):
        self.action_abstracter = ActionAbstracter()
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        min_val = 0
        max_val = 0
        actionTuple = []
        #print(round_state)
        for each in valid_actions:
            if each["action"] == "raise":
                min_val = each["amount"]["min"]
                max_val = each["amount"]["max"]
            elif each["action"] == "call":
                actionTuple.append((each["action"], each["amount"]))
        raise_actions = self.action_abstracter.get_abstracted_raise_values(min_val, round_state["pot"]["main"]["amount"], max_val)
        for each in raise_actions:
            actionTuple.append(("raise", each))
        chosen_action = random.choice(actionTuple)#valid_actions[1]["action"], valid_actions[1]["amount"]#
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        return chosen_action  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass