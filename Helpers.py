import _pickle as pickle
import os
from InformationAbstracter import InformationAbstracter


class HelperClass:
    # to be used while updating trees after each game during training
    def __init__(self):
        self.information_abstracter = InformationAbstracter()
        self.rotation_dict = {"p1": 0, "p2": 1, "p3": 2, "p4": 3, "p5": 4, "p6": 5}
        self.finalRound = ""
    @staticmethod
    def update_tree(tree, tree_name):
        with open(tree_name, 'wb') as file:
            file.write(pickle.dumps(tree))

    def agentTreeUpdater(self, move, hole_card, round_state, name, cards):
        action_history = round_state["action_histories"]
        self.finalRound = list(action_history.keys())[-1]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])
        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind)
        actionsTree = self.traverseAndUpdateAgentMove(playerIdMap, actionsTree, action_history, cards, move)
        self.update_tree(actionsTree, file_path)
        return actionsTree, file_path

    def tree_builder(self, name, card_history, hole_card, round_state):
        action_history = round_state["action_histories"]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        small_blind = playerIdMap.get(action_history["preflop"][0]["uuid"])

        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, "preflop",
                                                                              small_blind)
        actionsTree = self.updateChildDicts(playerIdMap, actionsTree, action_history,  card_history)
        self.update_tree(actionsTree, file_path)

    def updateChildDicts(self, playerIdMap, actionTree, action_history, cardsHist):
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
            moveId = moves[0]["action"] + "-" + str(moves[0]["amount"])
        if playerId != "p1":
            if not actionTree.get(playerId):
                actionTree[playerId] = {}
            if moveId in actionTree[playerId]:
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][moveId] = self.updateChildDicts(playerIdMap,
                                                                         actionTree[playerId][moveId], action_history,
                                                                         cardsHist)
            else:
                actionTree[playerId][moveId] = {}
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][moveId] = self.updateChildDicts(playerIdMap,
                                                                         actionTree[playerId][moveId], action_history,
                                                                         cardsHist)
        else:
            #print(playerId, moveId, round, actionTree, action_history)
            if round == "preflop":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    if playerId in actionTree:
                        if moveId in actionTree[playerId]:
                            actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                    actionTree[playerId][moveId][1][
                                                                                        moveId], action_history,
                                                                                    cardsHist)
                        else:
                            actionTree[playerId][moveId] = [0,{}]
                            actionTree[playerId][moveId][1][moveId] = {}
                            actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                            actionTree[playerId][
                                                                                                moveId][1][
                                                                                                moveId], action_history,
                                                                                            cardsHist)
                    else:
                        actionTree[playerId] = {}
                        actionTree[playerId][moveId] = [0, {}]
                        actionTree[playerId][moveId][1][moveId] = {}
                        actionTree[playerId][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                        actionTree[playerId][
                                                                                            moveId][1][
                                                                                            moveId], action_history,
                                                                                        cardsHist)
            else:
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                if len(action_history) > 0:
                    actionTree[playerId][cardsHist[round]][moveId][1][moveId] = self.updateChildDicts(playerIdMap,
                                                                                                      actionTree[
                                                                                                          playerId][
                                                                                                          cardsHist[
                                                                                                              round]][
                                                                                                          moveId][1][
                                                                                                          moveId],
                                                                                                      action_history,
                                                                                                      cardsHist)
        return actionTree

    def traverseAndUpdateAgentMove(self, playerIdMap, actionTree, action_history, cardsHist, move):
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
                moveId = moves[0]["action"] + "-" + str(moves[0]["amount"])
        else:
            playerId = "p1"
        if playerId != "p1":
            del action_history[round][0]
            if len(action_history[round]) == 0:
                del action_history[round]
            actionTree[playerId][moveId] = self.traverseAndUpdateAgentMove(playerIdMap,
                                                                               actionTree[playerId][moveId],
                                                                               action_history, cardsHist, move)
        else:
            if playerId not in actionTree.keys():
                actionTree[playerId] = {}
            if round == "preflop":
                if len(moves) > 0 and moveId in actionTree[playerId].keys():
                    if moveId in actionTree[playerId][moveId][1]:
                        if playerId == "p1":
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
                                    action_history, cardsHist, move)
                        else:
                            if len(action_history) > 0:
                                actionTree[playerId][moveId][1][moveId] = self.traverseAndUpdateAgentMove(
                                    playerIdMap,
                                    actionTree[
                                        playerId][
                                        moveId][
                                        1][
                                        moveId],
                                    action_history, cardsHist, move)
                else:
                    actionTree[playerId][move] = [0, {}]
                    actionTree[playerId][move][1][move] = {}
                    if len(action_history) > 0:
                        actionTree[playerId][move][1][move] = self.traverseAndUpdateAgentMove(
                            playerIdMap,
                            actionTree[
                                playerId][
                                move][1][
                                move], action_history, cardsHist, move)

            else:
                print(cardsHist[round], actionTree[playerId])
                key = self.getKey(cardsHist[round], actionTree[playerId])
                if len(moves)>0 and key != None and moveId in actionTree[playerId][
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
                                    action_history, cardsHist, move)
                        else:
                            if len(action_history) > 0:
                                actionTree[playerId][key][moveId][1][
                                    moveId] = self.self.traverseAndUpdateAgentMove(
                                    playerIdMap,

                                    actionTree[playerId][
                                        key][moveId][1][
                                        moveId],
                                    action_history, cardsHist, move)
                elif key != None and move not in actionTree[playerId][key]:

                    actionTree[playerId][key][move][1] = [0, {}]
                    actionTree[playerId][key][move][1][move] = {}
                    if playerId == "p1":
                        del action_history[round][0]
                        if len(action_history[round]) == 0:
                            del action_history[round]
                        if len(action_history) > 0:
                            actionTree[playerId][key][move][1][
                                move] = self.self.traverseAndUpdateAgentMove(

                                playerIdMap,
                                actionTree[
                                    playerId][key][move][1][move]
                                ,
                                action_history, cardsHist, move)
                    else:
                        if len(action_history) > 0:
                            actionTree[playerId][key][1][move] = self.self.traverseAndUpdateAgentMove(

                                playerIdMap,

                                actionTree[
                                    playerId][
                                    key][
                                    1][
                                    move],
                                action_history, cardsHist, move)
                else:
                    actionTree[playerId][cardsHist[round]] = {}
                    actionTree[playerId][cardsHist[round]][move] = [0, {}]
                    actionTree[playerId][cardsHist[round]][move][1][move] = {}
                    if playerId == "p1" and round != self.finalRound:
                        del action_history[round][0]
                        if len(action_history[round]) == 0:
                            del action_history[round]
                        if len(action_history) > 0:
                            actionTree[playerId][cardsHist[round]][move][1][
                                move] = self.self.traverseAndUpdateAgentMove(

                                playerIdMap,
                                actionTree[
                                    playerId][cardsHist[round]][move][1][move]
                                ,
                                action_history, cardsHist, move)
                    else:
                        if len(action_history) > 0:
                            print(action_history)
                            if playerId not in actionTree.keys():
                                actionTree[playerId] = {}
                            key = self.getKey(cardsHist[round], actionTree[playerId])
                            if key not in actionTree[playerId].keys():
                                actionTree[playerId][cardsHist[round]] = {}
                            if move not in actionTree[playerId][cardsHist[round]].keys():
                                actionTree[playerId][cardsHist[round]][move] = [0, {}]
                            if move not in actionTree[playerId][cardsHist[round]][move][1].keys():
                                actionTree[playerId][cardsHist[round]][move][1][move] = {}
                            if len(moves) > 0:
                                actionTree[playerId][cardsHist[round]][move][1][move] = self.traverseAndUpdateAgentMove(

                                playerIdMap,

                                actionTree[
                                    playerId][
                                    cardsHist[round]][move][
                                    1][
                                    move],
                                action_history, cardsHist, move)

        return actionTree

    def getKey(self, cards, dictToCheck):
        for each in dictToCheck.items():
            if set(cards) == set(each[0]):
                return each[0]

    def updateNetVal(self, actions_tree, round_state, cardsHist, name, final_move, net_val, file):
        action_history = round_state["action_histories"]
        final_round = round_state["street"]
        rotation_value = self.rotation_dict.get(name)
        playerIdMap = {}
        for each in round_state["seats"]:
            index = round_state["seats"].index(each)
            playerIdMap[each["uuid"]] = round_state["seats"][index - rotation_value]["name"]
        actions_tree = self.traverseAndUpdateVal(actions_tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move)
        self.update_tree(actions_tree, file)

    def traverseAndUpdateVal(self, tree, action_history, playerIdMap, cardsHist, net_val, final_round, final_move):
        if len(action_history) > 0:
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
                moveId = moves[0]["action"] + "-" + str(moves[0]["amount"])
            if playerId != "p1":
                del action_history[round][0]
                if len(action_history[round]) == 0:
                    del action_history[round]
                tree[playerId][moveId] = self.traverseAndUpdateVal(tree[playerId][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move)
            else:
                if round == "preflop":
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        tree[playerId][moveId][0] = tree[playerId][moveId][0] + net_val
                        tree[playerId][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move)
                else:
                    del action_history[round][0]
                    if len(action_history[round]) == 0:
                        del action_history[round]
                    if len(action_history) > 0:
                        key = self.getKey(cardsHist[round], tree[playerId])
                        tree[playerId][key][moveId][0] = tree[playerId][key][moveId][0] + net_val
                        tree[playerId][key][moveId][1][moveId] = self.traverseAndUpdateVal(tree[playerId][key][moveId][1][moveId],action_history,playerIdMap,cardsHist, net_val, final_round, final_move)
        else:
            if final_round == "preflop":
                if "terminal_val" in tree["p1"][final_move][1][final_move].keys():
                    tree["p1"][final_move][1][final_move]["terminal_val"] = tree["p1"][final_move][1][final_move]["terminal_val"] + net_val
                else:
                    tree["p1"][final_move][1][final_move]["terminal_val"] = net_val
            else:
                if "terminal_val" in tree["p1"][self.getKey(cardsHist[final_round], tree["p1"])][final_move][1][final_move].keys():
                    tree["p1"][self.getKey(cardsHist[final_round], tree["p1"])][final_move][1][final_move]["terminal_val"] = tree["p1"][self.getKey(cardsHist[final_round], tree["p1"])][final_move][1][final_move]["terminal_val"] + net_val
                else:
                    tree["p1"][self.getKey(cardsHist[final_round], tree["p1"])][final_move][1][final_move]["terminal_val"] = net_val
        return tree