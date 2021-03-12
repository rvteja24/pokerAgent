# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:38:04 2021

@author: vijaya_rayavarapu
"""

from pypokerengine.players import BasePokerPlayer
from Helpers import HelperClass

class Agent(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    def __init__(self):
        self.tree = {}
        self.helper = HelperClass()
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        print(valid_actions)
        self.helper.tree_builder(valid_actions, hole_card, round_state)
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

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