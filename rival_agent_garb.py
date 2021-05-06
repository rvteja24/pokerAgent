# Agent reference taken from https://github.com/3243-poker/poker-agent and modifications have been made for 6 pla


from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import testrun
import random

NB_SIMULATION = 2


class TrainedPlayer(BasePokerPlayer):
    coeff = [0, 0, 0, 0, 0]  # curr_round, money_diff, curr_street, rng, win_rate

    def __init__(self):
        self.coeff = [0, 0, 0.2302552184650441, 0.49392940373345967, 0.33366560185312216]
        self.curr_round = 0
        self.curr_money_diff = 0
        self.curr_street = 0
        self.rng = 0
        self.win_rate = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        self.rng = random.randint(0, 10)
        community_card = round_state['community_card']
        self.win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        act = 0
        act += self.coeff[0] * self.curr_round
        act += self.coeff[1] * self.curr_money_diff
        act += self.coeff[2] * self.curr_street
        act += self.coeff[3] * self.rng
        act += self.coeff[4] * self.win_rate
        # print(act)
        if act > 2 and len(valid_actions) == 3:
            action = valid_actions[2]
            amount = valid_actions[2]["amount"]["min"]
        elif act > 1:
            action = valid_actions[1]
            amount = valid_actions[1]["amount"]
        else:
            action = valid_actions[0]
            amount = 0
        # print(action['action'])
        return action['action'], amount
        '''
        if win_rate >= 0.66 and len(valid_actions) == 3:
            action = valid_actions[2]
        elif win_rate >= 0.33:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info
        return action['action']
        '''

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.current_round = round_count
        pass

    def receive_street_start_message(self, street, round_state):
        if street == "preflop":
            self.curr_street = 1
        elif street == "flop":
            self.curr_street = 2
        elif street == "turn":
            self.curr_street = 3
        elif street == "river":
            self.curr_street = 4

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        player1 = round_state["seats"][0]["stack"]
        player2 = round_state["seats"][1]["stack"]
        player3 = round_state["seats"][2]["stack"]
        player4 = round_state["seats"][3]["stack"]
        player5 = round_state["seats"][4]["stack"]
        # player6 = round_state["seats"][5]["stack"]
        p_avg = (player1 + player2 + player3 + player5)/4
        self.curr_money_diff = player4 - p_avg  # I assume I'm always player 2.
        # print(curr_money_diff)
