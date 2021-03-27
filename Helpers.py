import _pickle as pickle
import os
from math import ceil

from treys import Card as card
from treys import Evaluator
from InformationAbstracter import InformationAbstracter
from ActionAbstracter import ActionAbstracter

class HelperClass:
    # to be used while updating trees after each game during training
    def __init__(self):
        self.information_abstracter = InformationAbstracter()
        self.action_abstracter = ActionAbstracter()
        self.rotation_dict = {"p1": 0, "p2": 1, "p3": 2, "p4": 3, "p5": 4, "p6": 5}
        self.finalRound = ""
        self.evaluator = Evaluator()
        with open("cardMap.dict", "rb") as file:
            self.cardMap = pickle.loads(file.read())

    @staticmethod
    def update_tree(tree, tree_name):
        with open(tree_name, 'wb') as file:
            file.write(pickle.dumps(tree))

    def agentTreeUpdater(self, move, hole_card, round_state, name, cards):
        action_history = round_state["action_histories"]
        self.finalRound = list(action_history.keys())[-1]
        rotation_value = self.rotation_dict.get(name)
        # to do: use in future to handle unknown player names
        # game_to_known = {}
        # for i, each in enumerate(round_state["seats"]):
        #     game_to_known[each["name"]] = "p" + str(i+1)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])
        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind)
        stacks = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            stacks[each["uuid"]] = round_state["seats"][index - rotation_value]["stack"]
        pot = 0
        actionsTree = self.traverseAndUpdateAgentMove(playerIdMap, actionsTree, action_history, cards, move, pot, stacks)
        self.update_tree(actionsTree, file_path)
        return actionsTree, file_path

    def tree_builder(self, name, card_history, hole_card, round_state):
        action_history = round_state["action_histories"]
        current_round = round_state["street"]
        rotation_value = self.rotation_dict.get(name)
        # to do: use in future to handle unknown player names
        # game_to_known = {}
        # for i, each in enumerate(round_state["seats"]):
        #     game_to_known[each["name"]] = "p" + str(i+1)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])

        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind)
        stacks = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            stacks[each["uuid"]] = round_state["seats"][index - rotation_value]["stack"]
        pot_val = 0
        actionsTree = self.updateChildDicts(playerIdMap, actionsTree, action_history,  card_history, current_round, pot_val, stacks)
        self.update_tree(actionsTree, file_path)

    def updateChildDicts(self, playerIdMap, actionTree, action_history, cardsHist, current_round, pot_val, stacks):
        if action_history:
            round = list(action_history.keys())[0]
            moves = action_history.get(round)
            if len(moves) > 0:
                playerId = playerIdMap[moves[0]["uuid"]]
            else:
                return actionTree
        else:
            return actionTree

        if moves[0]["action"] == "FOLD":
            moveId = "FOLD"
        elif moves[0]["action"] == "CALL":
            moveId = "CALL"
        elif moves[0]["action"] == "BIGBLIND":
            moveId = "BIGBLIND"
        elif moves[0]["action"] == "SMALLBLIND":
            moveId = "SMALLBLIND"
        else:
            raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pot_val, round,
                                                                         stacks[moves[0]["uuid"]])
            moveId = moves[0]["action"] + "-" + str(raise_prop)

        if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
            pot_val += moves[0]["paid"]
            stacks[moves[0]["uuid"]] -= moves[0]["paid"]
        elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
            pot_val += moves[0]["amount"]
            stacks[moves[0]["uuid"]] -= moves[0]["amount"]
        if playerId != "p1":
            if not actionTree.get(playerId):
                actionTree[playerId] = {}
            if moveId in actionTree[playerId].keys():
                if current_round == round:
                    actionTree[playerId][moveId][0] += 1
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][moveId][1] = self.updateChildDicts(playerIdMap,
                                                                         actionTree[playerId][moveId][1], action_history,
                                                                         cardsHist,current_round, pot_val, stacks)
            else:
                actionTree[playerId][moveId] = [1,{}]
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][moveId][1] = self.updateChildDicts(playerIdMap,
                                                                         actionTree[playerId][moveId][1], action_history,
                                                                         cardsHist,current_round, pot_val, stacks)
        else:
            #print(playerId, moveId, round, actionTree, action_history)
            if round == "preflop":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    if playerId in actionTree:
                        if moveId in actionTree[playerId].keys():
                            actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                    actionTree[playerId][moveId][1][moveId], action_history,
                                                                                    cardsHist,current_round, pot_val, stacks)
                        else:
                            actionTree[playerId][moveId] = [(0,0),{}]
                            actionTree[playerId][moveId][1][moveId] = {}
                            actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                            actionTree[playerId][
                                                                                                moveId][1][moveId], action_history,
                                                                                            cardsHist,current_round, pot_val, stacks)
                    else:
                        actionTree[playerId] = {}
                        actionTree[playerId][moveId] = [(0,0), {}]
                        actionTree[playerId][moveId][1][moveId] = {}
                        actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                        actionTree[playerId][moveId][1][moveId]
                                                                                            , action_history,
                                                                                        cardsHist,current_round, pot_val, stacks)
            else:
                key = self.getKey(cardsHist[round])
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][key][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                                      actionTree[
                                                                                                          playerId][key][
                                                                                                          moveId][1][
                                                                                                          moveId],
                                                                                                      action_history,
                                                                                                      cardsHist,current_round, pot_val, stacks)
        return actionTree

    def traverseAndUpdateAgentMove(self, playerIdMap, actionTree, action_history, cardsHist, move, pot_val, stacks):
        #print("inside agent", action_history)
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
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pot_val, round, stacks[moves[0]["uuid"]])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[moves[0]["uuid"]] -= moves[0]["paid"]
                pot_val += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                stacks[moves[0]["uuid"]] -= moves[0]["amount"]
                pot_val += moves[0]["amount"]
        else:
            # moveSplit = move.split("-")
            # if moveSplit[0] == "RAISE":
            #     move = moveSplit[0] + "-" + str(float(moveSplit[-1])/pot_val)
            # else:
            #     move = moveSplit[0]
            # pot_val += float(moveSplit[-1])
            playerId = "p1"
        if playerId != "p1":
            del action_history[round][0]
            if len(action_history[round]) == 0:
                del action_history[round]
            actionTree[playerId][moveId][1] = self.traverseAndUpdateAgentMove(playerIdMap,
                                                                               actionTree[playerId][moveId][1],
                                                                                action_history, cardsHist, move, pot_val, stacks)
        else:
            if "CALL" in move or "FOLD" in move:
                move = move[:4]
            if playerId not in actionTree.keys():
                actionTree[playerId] = {}
            if round == "preflop":
                if len(moves) > 0 and moveId in actionTree[playerId].keys():
                    # if moveId in actionTree[playerId][moveId][1]:
                    # if playerId == "p1":
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
                    # else:
                    #     if len(action_history) > 0:
                    #         actionTree[playerId][moveId][1][moveId] = self.traverseAndUpdateAgentMove(
                    #             playerIdMap,
                    #             actionTree[
                    #                 playerId][
                    #                 moveId][
                    #                 1][
                    #                 moveId],
                    #             action_history, cardsHist, move, pot_val)
                elif len(moves) == 0 and move not in actionTree[playerId].keys():
                    actionTree[playerId][move] = [(0,0), {}]
                    actionTree[playerId][move][1][move] = {}
                    if len(action_history) > 0:
                        actionTree[playerId][move][1][move] = self.traverseAndUpdateAgentMove(
                            playerIdMap,
                            actionTree[
                                playerId][
                                move][1][
                                move], action_history, cardsHist, move, pot_val, stacks)

            else:
                #print(cardsHist[round], actionTree[playerId])
                key = self.getKey(cardsHist[round])
                if len(moves)>0 and key in actionTree[playerId] and moveId in actionTree[playerId][
                    key]:
                    if moveId in actionTree[playerId][key][moveId][1]:
                        if playerId == "p1":
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
                        # else:
                        #     if len(action_history) > 0:
                        #         actionTree[playerId][key][moveId][1][
                        #             moveId] = self.traverseAndUpdateAgentMove(
                        #             playerIdMap,
                        #
                        #             actionTree[playerId][
                        #                 key][moveId][1][
                        #                 moveId],
                        #             action_history, cardsHist, move, pot_val)
                elif key in actionTree[playerId] and move not in actionTree[playerId][key]:
                    actionTree[playerId][key][move] = [(0,0), {}]
                    actionTree[playerId][key][move][1][move] = {}
                    if playerId == "p1" and len(action_history) > 0 and len(action_history[round]) > 0:
                        del action_history[round][0]
                        if len(action_history[round]) == 0:
                            del action_history[round]
                        if len(action_history) > 0:
                            actionTree[playerId][key][move][1][
                                move] = self.traverseAndUpdateAgentMove(

                                playerIdMap,
                                actionTree[
                                    playerId][key][move][1][move]
                                ,
                                action_history, cardsHist, move, pot_val, stacks)
                    # else:
                    #     if len(action_history) > 0:
                    #         actionTree[playerId][key][1][move] = self.traverseAndUpdateAgentMove(
                    #
                    #             playerIdMap,
                    #
                    #             actionTree[
                    #                 playerId][
                    #                 key][
                    #                 1][
                    #                 move],
                    #             action_history, cardsHist, move, pot_val)
                elif key not in actionTree[playerId].keys():
                    actionTree[playerId][key] = {}
                    actionTree[playerId][key][move] = [(0,0), {}]
                    actionTree[playerId][key][move][1][move] = {}
                    if playerId == "p1" and round != self.finalRound:
                        del action_history[round][0]
                        if len(action_history[round]) == 0:
                            del action_history[round]
                        if len(action_history) > 0:
                            actionTree[playerId][key][move][1][
                                move] = self.traverseAndUpdateAgentMove(

                                playerIdMap,
                                actionTree[
                                    playerId][key][move][1][move]
                                ,
                                action_history, cardsHist, move, pot_val, stacks)
                    else:
                        if len(action_history) > 0:
                            #print(action_history)
                            if playerId not in actionTree.keys():
                                actionTree[playerId] = {}
                            key = self.getKey(cardsHist[round])
                            if key not in actionTree[playerId].keys():
                                actionTree[playerId][key] = {}
                            if move not in actionTree[playerId][key].keys():
                                actionTree[playerId][key][move] = [(0,0), {}]
                            if move not in actionTree[playerId][key][move][1].keys():
                                actionTree[playerId][key][move][1][move] = {}
                            if len(moves) > 0:
                                actionTree[playerId][key][move][1][move] = self.traverseAndUpdateAgentMove(

                                playerIdMap,

                                actionTree[
                                    playerId][key][move][
                                    1][
                                    move],
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
        return str(ceil(eval/40))

    def updateNetVal(self, actions_tree, round_state, cardsHist, name, final_move, net_val, file):
        action_history = round_state["action_histories"]
        final_round = round_state["street"]
        rotation_value = self.rotation_dict.get(name)
        # to do: use in future to handle unknown player names
        # game_to_known = {}
        # for i, each in enumerate(round_state["seats"]):
        #     game_to_known[each["name"]] = "p" + str(i+1)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        stacks = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            stacks[each["uuid"]] = round_state["seats"][index - rotation_value]["stack"]
        pot_value = 0
        actions_tree = self.traverseAndUpdateVal(actions_tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move, pot_value, stacks)
        self.update_tree(actions_tree, file)

    def traverseAndUpdateVal(self, tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move, pot_value, stacks):
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
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pot_value, round,
                                                                             stacks[moves[0]["uuid"]])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[moves[0]["uuid"]] -= moves[0]["paid"]
                pot_value += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                stacks[moves[0]["uuid"]] -= moves[0]["amount"]
                pot_value += moves[0]["amount"]
            if playerId != "p1":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                tree[playerId][moveId][1] = self.traverseAndUpdateVal(tree[playerId][moveId][1],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks)
            else:
                if round == "preflop":
                    count = tree[playerId][moveId][0][0]
                    val = ((tree[playerId][moveId][0][1] * count) + net_val) / (count + 1)
                    tree[playerId][moveId][0] = (count + 1, val)
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree[playerId][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks)
                else:
                    key = self.getKey(cardsHist[round])
                    count = tree[playerId][key][moveId][0][0]
                    val = ((tree[playerId][key][moveId][0][1] * count) + net_val) / (count + 1)
                    tree[playerId][key][moveId][0] = (count + 1, val)
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree[playerId][key][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][key][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move, pot_value, stacks)
        else:
            if "CALL" in final_move or "FOLD" in final_move:
                final_move = final_move[:4]
            # moveSplit = final_move.split("-")
            # if moveSplit[0] == "RAISE":
            #     final_move = moveSplit[0] + "-" + str(float(moveSplit[-1]) / pot_value)
            # else:
            #     final_move = moveSplit[0]
            # pot_value += float(moveSplit[-1])
            if final_round == "preflop":
                count = tree["p1"][final_move][0][0] + 1
                tree["p1"][final_move][0] = (count, ((tree["p1"][final_move][0][1] *(count-1) )+ net_val)/count)
                # tree["p1"][final_move][1] = "terminal_node"
            else:
                key = self.getKey(cardsHist[final_round])
                count = tree["p1"][key][final_move][0][0] + 1
                val = ((tree["p1"][key][final_move][0][1] * (count-1)) + net_val)/count
                tree["p1"][key][final_move][0] = (count, val)
                # tree["p1"][key][final_move][1] = "terminal_node"
        return tree

    def traverseAndReturnExploredActions(self, round_state, name, hole_card, cardsHist):
        action_history = round_state["action_histories"]
        rotation_value = self.rotation_dict.get(name)
        # to do: use in future to handle unknown player names
        # game_to_known = {}
        # for i, each in enumerate(round_state["seats"]):
        #     game_to_known[each["name"]] = "p" + str(i+1)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])

        stacks = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            stacks[each["uuid"]] = round_state["seats"][index - rotation_value]["stack"]

        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind)
        pots = 0
        return self.traverser(actionsTree, action_history, playerIdMap, cardsHist, pots, stacks)

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
                raise_prop = self.action_abstracter.get_mappable_raise_value(moves[0]["amount"], pots, round, stacks[moves[0]["uuid"]])
                moveId = moves[0]["action"] + "-" + str(raise_prop)
            if moves[0]["action"] != "FOLD" and "paid" in moves[0].keys():
                stacks[moves[0]["uuid"]] -= moves[0]["paid"]
                pots += moves[0]["paid"]
            elif moves[0]["action"] == "BIGBLIND" or moves[0]["action"] == "SMALLBLIND":
                stacks[moves[0]["uuid"]] -= moves[0]["amount"]
                pots += moves[0]["amount"]
            if playerId != "p1":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                tree = self.traverser(tree[playerId][moveId][1],action_history,playerIdMap,cardsHist, pots, stacks)
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
        else:
            return tree
        return tree