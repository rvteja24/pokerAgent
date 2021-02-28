# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:46:17 2021

@author: vijaya_rayavarapu
"""
# actions : raise, call, fold
#if raise is selected valid amount is to be entered
import pypokerengine.utils.visualize_utils as U
from pypokerengine.players import BasePokerPlayer
class HumanPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid))
        action, amount = self._receive_action_from_console(valid_actions)
        return action, amount

    def receive_game_start_message(self, game_info):
        print(U.visualize_game_start(game_info, self.uuid))
        self._wait_until_input()

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(U.visualize_round_start(round_count, hole_card, seats, self.uuid))
        self._wait_until_input()

    def receive_street_start_message(self, street, round_state):
        print(U.visualize_street_start(street, round_state, self.uuid))
        self._wait_until_input()

    def receive_game_update_message(self, new_action, round_state):
        print(U.visualize_game_update(new_action, round_state, self.uuid))
        self._wait_until_input()

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))
        self._wait_until_input()

    def _wait_until_input(self):
        input("Enter some key to continue ...")

    # FIXME: This code would be crash if receives invalid input.
    #        So you should add error handling properly.
    def _receive_action_from_console(self, valid_actions):
        action = input("Enter action to declare >> ")
        if action == 'fold': amount = 0
        if action == 'call':  amount = valid_actions[1]['action']
        if action == 'raise':  amount = int(input("Enter raise amount >> "))
        return action, amount