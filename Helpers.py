import _pickle as pickle
import os
from math import ceil

from treys import Card as card
from treys import Evaluator
from InformationAbstracter import InformationAbstracter
from ActionAbstracter import ActionAbstracter

class HelperClass:
    def __init__(self):
        self.information_abstracter = InformationAbstracter()
        self.action_abstracter = ActionAbstracter()
        self.rotation_dict = {"p1": 0, "p2": 1, "p3": 2, "p4": 3, "p5": 4, "p6": 5}
        self.finalRound = ""
        self.evaluator = Evaluator()
        self.p1_final_stack = 0
        self.traverser_stacks = {}
        self.tree = {}
        self.file_path = ""
        with open("cardMap.dict", "rb") as file:
            self.cardMap = pickle.loads(file.read())
            file.close()

    def reset(self):
        self.p1_final_stack = 0
        self.traverser_stacks = {}
        self.tree = {}
        self.file_path = ""
        self.finalRound = ""

    def update_tree(self, tree, tree_name):
        with open(tree_name, 'wb') as file:
            file.write(pickle.dumps(tree))
            file.close()
        self.reset()

    def agentTreeUpdater(self, move, hole_card, round_state, name, cards):
        action_history = round_state["action_histories"]
        self.finalRound = list(action_history.keys())[-1]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        # small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])
        # if round_state["street"] == "preflop":
        # self.tree, self.file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
        #                                                                       small_blind)
        stacks = {}
        for each in playerIdMap.values():
            stacks[each] = 10000
        pot = 0
        self.tree = self.traverseAndUpdateAgentMove(playerIdMap, self.tree, action_history, cards, move, pot, stacks)
        # self.update_tree(self.tree, self.file_path, hole_card, small_blind)
        return self.tree, self.file_path

    def traverseAndUpdateAgentMove(self, playerIdMap, actionTree, action_history, cardsHist, move, pot_val, stacks):
        if action_history:
            round = list(action_history.keys())[0]
            moves = action_history.get(round)
        else:
            round = self.finalRound
            moves = []
        if len(moves) > 0:
            playerId = playerIdMap[moves[0]["uuid"]]
            if moves[0]["action"] == "FOLD":
                moveId = "FOLD"
            elif moves[0]["action"] == "CALL":
                moveId = "CALL"
            elif moves[0]["action"] == "BIGBLIND":
                moveId = "BIGBLIND"
            elif moves[0]["action"] == "SMALLBLIND":
                moveId = "SMALLBLIND"
            else:
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pot_val, round, stacks[playerId])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[playerId] -= moves[0]["paid"]
                pot_val += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                stacks[playerId] -= moves[0]["amount"]
                pot_val += moves[0]["amount"]
        else:
            playerId = "p1"
            moveId = move
            if "CALL" in move or "FOLD" in move:
                moveId = move[:4]
        if playerId != "p1":
            if playerId not in actionTree:
                actionTree[playerId] = {}
            if moveId not in actionTree[playerId]:
                actionTree[playerId][moveId] = [1, {}]
            else:
                actionTree[playerId][moveId][0] += 1
            del action_history[round][0]
            if len(action_history[round]) == 0:
                del action_history[round]
            actionTree[playerId][moveId][1] = self.traverseAndUpdateAgentMove(playerIdMap,
                                                                               actionTree[playerId][moveId][1],
                                                                                action_history, cardsHist, move, pot_val, stacks)
        else:
            if playerId not in actionTree.keys():
                actionTree[playerId] = {}
            if round == "preflop":
                if moveId not in actionTree[playerId].keys():
                    actionTree[playerId][moveId] = [(0,0), {}]
                    actionTree[playerId][moveId][1][moveId] = {}
                if len(moves) > 0:
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        actionTree[playerId][moveId][1][moveId] = self.traverseAndUpdateAgentMove(
                        playerIdMap,
                        actionTree[
                            playerId][
                            moveId][
                            1][
                            moveId],
                        action_history, cardsHist, move, pot_val, stacks)
            else:
                key = self.getKey(cardsHist[round])
                if key not in actionTree[playerId].keys():
                    actionTree[playerId][key] = {}
                if moveId not in actionTree[playerId][key].keys():
                    actionTree[playerId][key][moveId] = [(0, 0), {}]
                if moveId not in actionTree[playerId][key][moveId][1].keys():
                    actionTree[playerId][key][moveId][1][moveId] = {}
                if len(moves) > 0:
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        actionTree[playerId][key][moveId][1][
                        moveId] = self.traverseAndUpdateAgentMove(
                        playerIdMap,

                        actionTree[
                            playerId][
                            key][moveId][
                            1][
                            moveId],
                        action_history, cardsHist, move, pot_val, stacks)
        return actionTree

    def getKey(self, cards):
        board = []
        hand = []
        for e in cards[0]:
            board.append(card.new(self.cardMap.get(e)))
        for e in cards[1]:
            hand.append(card.new(self.cardMap.get(e)))
        eval = self.evaluator.evaluate(hand, board)
        return str(ceil(eval/39))

    def updateNetVal(self, hole_cards, round_state, cardsHist, name, final_move, net_val):
        action_history = round_state["action_histories"]
        final_round = round_state["street"]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        stacks = {}
        for each in playerIdMap.values():
            stacks[each] = 10000
        pot_value = 0
        previous_amount = 0
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])
        # self.tree, self.file_path = self.information_abstracter.get_tree_details(hole_cards, "preflop",
        #                                                                       small_blind)
        self.tree = self.traverseAndUpdateVal(self.tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move, pot_value, stacks, previous_amount)
        self.update_tree(self.tree, self.file_path)

    def traverseAndUpdateVal(self, tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move, pot_value, stacks, previous_amount):
        if action_history:
            round = list(action_history.keys())[0]
            moves = action_history.get(round)
        else:
            round = self.finalRound
            moves = []
        if len(moves) > 0:
            playerId = playerIdMap[moves[0]["uuid"]]

            if moves[0]["action"] == "FOLD":
                moveId = "FOLD"
            elif moves[0]["action"] == "CALL":
                moveId = "CALL"
            elif moves[0]["action"] == "BIGBLIND":
                moveId = "BIGBLIND"
            elif moves[0]["action"] == "SMALLBLIND":
                moveId = "SMALLBLIND"
            else:
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pot_value, round,
                                                                             stacks[playerId])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
        else:
            playerId = "p1"
            moveId = final_move
            if "CALL" in final_move or "FOLD" in final_move:
                moveId = final_move[:4]
        if playerId != "p1":
            if moves[0]["action"] != "FOLD":
                previous_amount = moves[0]["amount"]
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[playerId] -= moves[0]["paid"]
                pot_value += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                stacks[playerId] -= moves[0]["amount"]
                pot_value += moves[0]["amount"]
            del action_history[round][0]
            if len(action_history[round]) == 0:
                del action_history[round]
            tree[playerId][moveId][1] = self.traverseAndUpdateVal(tree[playerId][moveId][1],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks, previous_amount)
        else:
            stack_val = stacks[playerId]
            #print(round, stack_val, moveId, previous_amount, pot_value)
            if round == "preflop":
                tree[playerId] = self.updateRegrets(tree[playerId], net_val, pot_value, moveId, stack_val, previous_amount)
                if len(moves) > 0:
                    if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                        stacks[playerId] -= moves[0]["paid"]
                        self.p1_final_stack = stacks[playerId]
                        pot_value += moves[0]["paid"]
                    elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                        stacks[playerId] -= moves[0]["amount"]
                        self.p1_final_stack = stacks[playerId]
                        pot_value += moves[0]["amount"]
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree[playerId][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks, previous_amount)
            else:
                key = self.getKey(cardsHist[round])
                tree[playerId][key] = self.updateRegrets(tree[playerId][key], net_val, pot_value, moveId, stack_val, previous_amount)
                if len(moves) > 0:
                    if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                        stacks[playerId] -= moves[0]["paid"]
                        self.p1_final_stack = stacks[playerId]
                        pot_value += moves[0]["paid"]
                    elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                        stacks[playerId] -= moves[0]["amount"]
                        self.p1_final_stack = stacks[playerId]
                        pot_value += moves[0]["amount"]
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree[playerId][key][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][key][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks, previous_amount)
        return tree

    def traverseAndReturnExploredActions(self, round_state, name, hole_card, cardsHist, version):
        action_history = round_state["action_histories"]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])

        if round_state["street"] == "preflop":
            for i, each in enumerate(round_state["seats"]):
                self.traverser_stacks[round_state["seats"][i - rotation_value]["name"]] = each["stack"]

        if round_state["street"] == "preflop":
            self.tree, self.file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind, version)
        pots = 0
        return self.traverser(self.tree, action_history, playerIdMap, cardsHist, pots, self.traverser_stacks)

    def traverser(self, tree, action_history, playerIdMap, cardsHist, pots, stacks):
        if len(action_history) > 0 and len(action_history.get(list(action_history.keys())[0], [])) > 0:
            round = list(action_history.keys())[0]
            moves = action_history.get(round)
            if len(moves)>0:
                playerId = playerIdMap[moves[0]["uuid"]]
            else:
                return tree
            if moves[0]["action"] == "FOLD":
                moveId = "FOLD"
            elif moves[0]["action"] == "CALL":
                moveId = "CALL"
            elif moves[0]["action"] == "BIGBLIND":
                moveId = "BIGBLIND"
            elif moves[0]["action"] == "SMALLBLIND":
                moveId = "SMALLBLIND"
            else:
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pots, round, stacks[playerId])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[playerId] -= moves[0]["paid"]
                pots += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                # stacks[playerId] -= moves[0]["amount"]
                pots += moves[0]["amount"]
            if playerId != "p1":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                tree = self.traverser(tree[playerId][moveId][1], action_history, playerIdMap,cardsHist, pots, stacks)
            else:
                if round == "preflop":
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree = self.traverser(tree[playerId][moveId][1][moveId],action_history,playerIdMap,cardsHist, pots, stacks)
                else:
                    key = self.getKey(cardsHist[round])
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree = self.traverser(tree[playerId][key][moveId][1][moveId], action_history,playerIdMap,cardsHist, pots, stacks)
        return tree

    def updateRegrets(self, tree, net_val, pot_val, final_move, stack, call_amount):
        if net_val != 0 and (final_move != "BIGBLIND" and final_move != "SMALLBLIND"):
            amount = 0
            if net_val < 0:
                net_val = net_val * 5
            if "RAISE" in final_move:
                splitMove = final_move.split("-")
                if splitMove[-1] == "allin":
                    amount = stack
                else:
                    amount = float(splitMove[-1]) * pot_val
            elif "CALL" in final_move:
                amount = call_amount
            elif "FOLD" in final_move:
                amount = net_val
            for each in tree.items():
                if each[0] == "CALL":
                    if call_amount == amount:
                        k = 1
                    else:
                        k = call_amount/amount
                    tree[each[0]][0] = (each[1][0][0], (1 * each[1][0][0]) +(net_val*((k)-1)))
                elif "RAISE" in each[0]:
                    splitMove = each[0].split("-")
                    sel_amount = 0
                    if splitMove[-1] == "allin":
                        sel_amount = stack
                    else:
                        sel_amount = float(splitMove[-1]) * pot_val
                    if amount == 0:
                        amount = 10000 - stack
                    tree[each[0]][0] = (each[1][0][0], (1 * each[1][0][0]) + (net_val * ((sel_amount/ amount) - 1)))
                elif each[0] == "FOLD":
                    tree[each[0]][0] = (each[1][0][0], (1 * each[1][0][0]) + (net_val * ( - 1)))
                if each[0] == final_move:
                    tree[each[0]][0] = (each[1][0][0] + 1, each[1][0][1])
        else:
            tree[final_move][0] = (tree[final_move][0][0] + 1, tree[final_move][0][1])
        return tree

