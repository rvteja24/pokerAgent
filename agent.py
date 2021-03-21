# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:38:04 2021

@author: vijaya_rayavarapu
"""

from pypokerengine.players import BasePokerPlayer
from Helpers import HelperClass
import copy
class Agent(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    def __init__(self, name="p1"):
        self.name = name
        self.tree = {}
        self.cardHist = {}
        self.helper = HelperClass()
        self.round_state_rest = {}
        self.round_state_agent = {}
        self.final_round = {}
        self.action_tree = {}
        self.file_path = ""
        self.final_move = ""
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):

        #print(round_state)
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.round_state_rest = copy.deepcopy(round_state)
        self.round_state_agent = copy.deepcopy(round_state)
        self.final_round = round_state
        #print("final round state----------------------------------", self.final_round)
        self.community_cards = copy.deepcopy(round_state["community_card"])
        while len(self.community_cards):
            self.cardHist[round_state["street"]] = tuple(self.community_cards + hole_card)
            self.community_cards = []
        self.helper.tree_builder(self.name, self.cardHist, hole_card, self.round_state_rest)
        # todo : come up with the logic based on how options are selected ad explored in MCCFR, for this to get all the raise actions possible we can use get abstracted raise values function present in action abstraction.
        # to get actions for a specific move and their values need to write a helper function to traverse and return the already present moves and their regret values.
        # convert raise values as proportion of pot values, so moves can be chosen based on pot value.

        self.action_tree, self.file_path = self.helper.agentTreeUpdater("CALL", hole_card, self.round_state_agent, self.name, self.cardHist)
        call_action_info = valid_actions[1]
        self.final_move = "CALL"
        action, amount = call_action_info["action"], call_action_info["amount"]
        # moves = [{"action": "CALL"}]
        # if moves[0]["action"] == "FOLD":
        #     moveId = "FOLD"
        # elif moves[0]["action"] == "CALL":
        #     moveId = "CALL"
        # else:
        #     moveId = moves[0]["action"] + "-" + str(moves[0]["amount"])
        #print(action, amount)
        return action, amount   # action returned here is sent to the poker engine

    def updateResult(self, game_result):
        final_stack = 0
        for i in game_result["players"]:
            if i["name"] == self.name:
                final_stack = i["stack"]
        initial_stack = game_result["rule"]["initial_stack"]
        net_val = final_stack - initial_stack
        #print("net val", net_val)
        self.helper.updateNetVal(self.action_tree, self.final_round, self.cardHist, self.name, self.final_move, net_val, self.file_path)
        #print(self.final_round, game_result)

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