# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:38:04 2021

@author: vijaya_rayavarapu
"""
import math
import random
import numpy as np
from pypokerengine.players import BasePokerPlayer

from ActionAbstracter import ActionAbstracter
from Helpers import HelperClass
import copy
class Agent(BasePokerPlayer):
    def __init__(self, name="p1"):
        self.name = name
        self.tree = {}
        self.cardHist = {}
        self.helper = HelperClass()
        self.round_state_rest = {}
        self.round_state_agent = {}
        self.round_state_eval = {}
        self.final_round = {}
        self.action_tree = {}
        self.file_path = ""
        self.final_move = ""
        self.action_abstracter = ActionAbstracter()
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        #action, amount = self.train(valid_actions, hole_card, round_state)
        print(self.name, "-----" ,hole_card)
        action, amount = self.test(valid_actions, hole_card, round_state)
        return action, amount

    def test(self, valid_actions, hole_card, round_state):
        self.round_state_eval = copy.deepcopy(round_state)
        self.community_cards = copy.deepcopy(round_state["community_card"])
        while len(self.community_cards):
            self.cardHist[round_state["street"]] = tuple((tuple(self.community_cards), tuple(hole_card)))
            self.community_cards = []
        min_val = 0
        max_val = 0
        actionTuple = {}
        for each in valid_actions:
            if each["action"] == "raise":
                min_val = each["amount"]["min"]
                max_val = each["amount"]["max"]
            else:
                actionTuple[(each["action"], each["amount"])] = (0, 0)
        raise_actions = self.action_abstracter.get_abstracted_raise_values(min_val,
                                                                           round_state["street"],
                                                                           max_val, round_state["pot"]["main"]["amount"])
        for each in raise_actions:
            actionTuple[("raise", each)] = (0, 0)
        try:
            explored_actions = self.helper.traverseAndReturnExploredActions(self.round_state_eval, self.name,
                                                                     hole_card, self.cardHist)


            if round_state["street"] == "preflop":
                explored_actions = explored_actions["p1"]
            else:
                key = self.helper.getKey(self.cardHist[round_state["street"]])
                explored_actions = explored_actions["p1"][key]
        except:
            explored_actions = {}
        explored_actions_tuple = []
        if explored_actions and len(explored_actions) > 0:
            #print(explored_actions)
            for each in explored_actions.keys():
                expl = each.split("-")
                act = expl[0].lower()
                if len(expl) == 2 and expl[-1] != "allin":
                    val = float(expl[-1])
                elif len(expl) == 2 and expl[-1] == "allin" :
                    val = expl[-1]
                else:
                    val = 0
                try:
                    explored_actions_tuple.append(((act, val), (explored_actions[each][0])))
                except:
                    print("Error in retrieving actions: ", explored_actions)

        stack_val = 0
        for each in round_state["seats"]:
            if each["name"] == self.name:
                stack_val = each["stack"]
                break

        for each in explored_actions_tuple:
            for e in actionTuple.items():
                if e[0][0] == each[0][0] and each[0][0] != "raise":
                    actionTuple[e[0]] = each[1]
                elif e[0] == each[0] and each[0][0] == "raise":
                    actionTuple[each[0]] = each[1]
                elif each[0][0] == "call" and each[0][1] > stack_val:
                    del explored_actions_tuple[each]
        best_move = self.action_picker(actionTuple, c = 0.0001)
        best_val = best_move[1]
        if best_move[0] == "raise":
            if best_move[1] == "allin":
                best_val = max_val
            else:
                best_val = best_move[1] * round_state["pot"]["main"]["amount"]
        action, amount = best_move[0], best_val
        return action, amount

    def train (self, valid_actions, hole_card, round_state):
        min_val = 0
        max_val = 0
        actionTuple = {}
        for each in valid_actions:
            if each["action"] == "raise":
                min_val = each["amount"]["min"]
                max_val = each["amount"]["max"]
            else:
                actionTuple[(each["action"], each["amount"])] = (0, 0)
        raise_actions = self.action_abstracter.get_abstracted_raise_values(min_val,
                                                                           round_state["street"],
                                                                           max_val, round_state["pot"]["main"]["amount"])
        for each in raise_actions:
            actionTuple[("raise", each)] = (0, 0)
        # print(round_state)
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.round_state_rest = copy.deepcopy(round_state)
        self.round_state_agent = copy.deepcopy(round_state)
        self.round_state_traversal = copy.deepcopy(round_state)
        self.final_round = copy.deepcopy(round_state)
        # print("final round state----------------------------------", self.final_round)
        self.community_cards = copy.deepcopy(round_state["community_card"])
        while len(self.community_cards):
            self.cardHist[round_state["street"]] = tuple((tuple(self.community_cards), tuple(hole_card)))
            self.community_cards = []
        self.helper.tree_builder(self.name, self.cardHist, hole_card, self.round_state_rest)
        # todo : come up with the logic based on how options are selected ad explored in MCCFR, for this to get all the raise actions possible we can use get abstracted raise values function present in action abstraction.
        # to get actions for a specific move and their values need to write a helper function to traverse and return the already present moves and their regret values.
        # convert raise values as proportion of pot values, so moves can be chosen based on pot value.
        try:
            explored_actions = self.helper.traverseAndReturnExploredActions(self.round_state_traversal, self.name,
                                                                     hole_card, self.cardHist)
            if round_state["street"] == "preflop":
                explored_actions = explored_actions["p1"]
            else:
                key = self.helper.getKey(self.cardHist[round_state["street"]])
                explored_actions = explored_actions["p1"][key]
        except:
            explored_actions = {}
        explored_actions_tuple = []
        if explored_actions and len(explored_actions) > 0:
            #print(explored_actions)
            for each in explored_actions.keys():
                expl = each.split("-")
                act = expl[0].lower()
                if len(expl) == 2 and expl[-1] != "allin":
                    val = float(expl[-1])
                elif len(expl) == 2 and expl[-1] == "allin" :
                    val = expl[-1]
                else:
                    val = 0
                try:
                    explored_actions_tuple.append(((act, val), (explored_actions[each][0])))
                except:
                    print("Error in retrieving actions: ", explored_actions)
        #print(explored_actions_tuple)
        stack_val = 0
        for each in round_state["seats"]:
            if each["name"] == self.name:
                stack_val = each["stack"]
                break
        for each in explored_actions_tuple:
            for e in actionTuple.items():
                #print(each)
                if e[0][0] == each[0][0] and each[0][0] != "raise":
                    actionTuple[e[0]] = each[1]
                    break
                elif e[0] == each[0] and each[0][0] == "raise":
                    #print(e[0], each[0], each[1], e[1])
                    actionTuple[each[0]] = each[1]
                    break
                # add the condition to avoid call when no stack enough for it
                elif each[0][0] == "call" and each[0][1] > stack_val:
                    del explored_actions_tuple[each]
        # best_move = random.choice(list(filter(lambda x: x[1][0] == 0, actionTuple.items())))[0]
        best_move = self.action_picker(actionTuple, c = 100000)

        if best_move[0].upper() == "FOLD":
            moveId = "FOLD-" + str(best_move[1])
        elif best_move[0].upper() == "CALL":
            moveId = "CALL-"+ str(best_move[1])
        else:
            moveId = best_move[0].upper() + "-" + str(best_move[1])
        self.action_tree, self.file_path = self.helper.agentTreeUpdater(moveId, hole_card, self.round_state_agent,
                                                                        self.name, self.cardHist)
        self.final_move = moveId
        best_val = best_move[1]
        if best_move[0] == "raise":
            if best_move[1] == "allin":
                best_val = max_val
            else:
                best_val = best_move[1] * round_state["pot"]["main"]["amount"]
        action, amount = best_move[0], best_val
        return action, amount  # action returned here is sent to the poker engine


    def updateResult(self, game_result):
        final_stack = 0
        for i in game_result["players"]:
            if i["name"] == self.name:
                final_stack = i["stack"]
                break
        initial_stack = game_result["rule"]["initial_stack"]
        net_val = final_stack - initial_stack
        #print("net val", net_val, self.final_move, self.final_round, self.name)
        if len(self.final_round) > 0 :
            self.helper.updateNetVal(self.action_tree, self.final_round, self.cardHist, self.name, self.final_move, net_val, self.file_path)
        self.reset()

    def reset(self):
        self.tree = {}
        self.cardHist = {}
        self.helper = HelperClass()
        self.round_state_rest = {}
        self.round_state_agent = {}
        self.round_state_eval = {}
        self.final_round = {}
        self.action_tree = {}
        self.file_path = ""
        self.final_move = ""

    def action_picker(self, actionTuple, c):
        #print(actionTuple)
        rewards = np.array([x[1][1] for x in actionTuple.items()])
        total_explorations = sum([x[1][0] for x in actionTuple.items()])
        exploration_value = np.array([c*((math.log(total_explorations)/x[1][0])**0.5) if x[1][0] > 0 else math.inf for x in actionTuple.items()])

        #print(rewards, exploration_value)
        selected_index = np.argmax(rewards + exploration_value)
        #print(actionTuple,list(actionTuple.keys())[selected_index])
        return list(actionTuple.keys())[selected_index]


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