# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:38:04 2021

@author: vijaya_rayavarapu
"""
import math
import random
from threading import Timer
import numpy as np
from pypokerengine.players import BasePokerPlayer
from ActionAbstracter import ActionAbstracter
from Helpers import HelperClass
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import copy


class Agent(BasePokerPlayer):
    def __init__(self, name="p1", version='latest'):
        self.name = name
        self.version = version
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
        # action, amount = self.train(valid_actions, hole_card, round_state)
        # print(self.name, "-----" ,round_state)
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
                                                                           max_val,
                                                                           round_state["pot"]["main"]["amount"])
        for each in raise_actions:
            actionTuple[("raise", each)] = (0, 0)
        try:
            explored_actions = self.helper.traverseAndReturnExploredActions(self.round_state_eval, self.name,
                                                                            hole_card, self.cardHist, self.version)

            if round_state["street"] == "preflop":
                explored_actions = explored_actions["p1"]
            else:
                key = self.helper.getKey(self.cardHist[round_state["street"]])
                explored_actions = explored_actions["p1"][key]
        except:
            explored_actions = {}
            with open("test.txt", "a") as f:
                f.write("No actions played yet: " + self.name + str(hole_card) + str(self.cardHist) + "\n")
                f.close()
            # print("No actions played yet", self.name, hole_card, self.cardHist)
        # if len(explored_actions) == 0:
        #     return self.mcts_search(hole_card, round_state, valid_actions)
        explored_actions_tuple = []
        if explored_actions and len(explored_actions) > 0:
            for each in explored_actions.keys():
                expl = each.split("-")
                act = expl[0].lower()
                if len(expl) == 2 and expl[-1] != "allin":
                    val = float(expl[-1])
                elif len(expl) == 2 and expl[-1] == "allin":
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
                    break
                elif e[0] == each[0] and each[0][0] == "raise":
                    actionTuple[each[0]] = each[1]
                    break
                elif each[0][0] == "call" and each[0][1] > stack_val:
                    del explored_actions_tuple[each]
                    break
        best_move = self.action_picker(actionTuple, c=0.0, replacement = 0)
        best_val = best_move[1]
        if best_move[0] == "raise":
            if best_move[1] == "allin":
                best_val = max_val
            else:
                best_val = best_move[1] * round_state["pot"]["main"]["amount"]
        action, amount = best_move[0], best_val
        return action, amount

    def train(self, valid_actions, hole_card, round_state):
        self.hole_card = hole_card
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
                                                                           max_val,
                                                                           round_state["pot"]["main"]["amount"])
        for each in raise_actions:
            actionTuple[("raise", each)] = (0, 0)
        self.round_state_rest = copy.deepcopy(round_state)
        self.round_state_agent = copy.deepcopy(round_state)
        self.round_state_traversal = copy.deepcopy(round_state)
        self.final_round = copy.deepcopy(round_state)
        self.community_cards = copy.deepcopy(round_state["community_card"])
        while len(self.community_cards):
            self.cardHist[round_state["street"]] = tuple((tuple(self.community_cards), tuple(hole_card)))
            self.community_cards = []
        try:
            explored_actions = self.helper.traverseAndReturnExploredActions(self.round_state_traversal, self.name,
                                                                            hole_card, self.cardHist, self.version)
            if round_state["street"] == "preflop":
                explored_actions = explored_actions["p1"]
            else:
                key = self.helper.getKey(self.cardHist[round_state["street"]])
                explored_actions = explored_actions["p1"][key]
        except:
            explored_actions = {}
            # with open("test.txt", "a") as f:
            #     f.write("No actions played yet: " + self.name + str(hole_card) + str(self.cardHist) + "\n")
            # print("No actions played yet", self.name, hole_card, self.cardHist)
        explored_actions_tuple = []
        if explored_actions and len(explored_actions) > 0:
            # print(explored_actions)
            for each in explored_actions.keys():
                expl = each.split("-")
                act = expl[0].lower()
                if len(expl) == 2 and expl[-1] != "allin":
                    val = float(expl[-1])
                elif len(expl) == 2 and expl[-1] == "allin":
                    val = expl[-1]
                else:
                    val = 0
                try:
                    explored_actions_tuple.append(((act, val), (explored_actions[each][0])))
                except:
                    print("Error in retrieving actions: ", explored_actions)
        # print(explored_actions_tuple)
        stack_val = 0
        for each in round_state["seats"]:
            if each["name"] == self.name:
                stack_val = each["stack"]
                break
        for each in explored_actions_tuple:
            for e in actionTuple.items():
                # print(each)
                if e[0][0] == each[0][0] and each[0][0] != "raise":
                    actionTuple[e[0]] = each[1]
                    break
                elif e[0] == each[0] and each[0][0] == "raise":
                    # print(e[0], each[0], each[1], e[1])
                    actionTuple[each[0]] = each[1]
                    break
                # add the condition to avoid call when no stack enough for it
                elif each[0][0] == "call" and each[0][1] > stack_val:
                    del explored_actions_tuple[each]
                    break
        # best_move = random.choice(list(filter(lambda x: x[1][0] == 0, actionTuple.items())))[0]
        # print(actionTuple)
        best_move = self.action_picker(actionTuple, c=1000000, replacement = math.inf)

        if best_move[0].upper() == "FOLD":
            moveId = "FOLD-" + str(best_move[1])
        elif best_move[0].upper() == "CALL":
            moveId = "CALL-" + str(best_move[1])
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
        # print("net val", net_val, self.final_move, self.final_round, self.name)
        if len(self.final_round) > 0:
            self.helper.updateNetVal(self.hole_card, self.final_round, self.cardHist, self.name, self.final_move,
                                     net_val)
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

    def action_picker(self, actionTuple, c, replacement):
        # print(actionTuple)
        rewards = np.array([x[1][1] for x in actionTuple.items()])
        total_explorations = sum([x[1][0] for x in actionTuple.items()])
        exploration_value = np.array(
            [c * ((math.log(total_explorations) / x[1][0]) ** 0.5) if x[1][0] > 0 else replacement for x in
             actionTuple.items()])

        # print(rewards, exploration_value)
        sum_arr = rewards + exploration_value
        selected_index = np.random.choice(np.flatnonzero(sum_arr == sum_arr.max()))
        # print(actionTuple,list(actionTuple.keys())[selected_index])
        return list(actionTuple.keys())[selected_index]

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def montecarlo_simulation(self, nb_player, hole_card, community_card):
        # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
        community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
        unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
        opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
        opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
        my_score = HandEvaluator.eval_hand(hole_card, community_card)
        return 1 if my_score >= max(opponents_score) else 0

    def estimate_win_rate(self, nb_simulation, nb_player, hole_card, community_card=None):
        if not community_card: community_card = []

        # Make lists of Card objects out of the list of cards
        community_card = gen_cards(community_card)
        hole_card = gen_cards(hole_card)

        # Estimate the win count by doing a Monte Carlo simulation
        win_count = sum([self.montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
        return 1.0 * win_count / nb_simulation

    def mcts_search(self, hole_card, round_state, valid_actions):
        win_rate = self.estimate_win_rate(1000, self.num_players, hole_card, round_state['community_card'])

        # Check whether it is possible to call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0

        amount = None

        # If the win rate is large enough, then raise
        if win_rate > 0.5:
            raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
            if win_rate > 0.85:
                # If it is extremely likely to win, then raise as much as possible
                action = 'raise'
                amount = raise_amount_options['max']
            elif win_rate > 0.75:
                # If it is likely to win, then raise by the minimum amount possible
                action = 'raise'
                amount = raise_amount_options['min']
            else:
                # If there is a chance to win, then call
                action = 'call'
        else:
            action = 'call' if can_call and call_amount == 0 else 'fold'

        # Set the amount
        if amount is None:
            items = [item for item in valid_actions if item['action'] == action]
            amount = items[0]['amount']

        return action, amount