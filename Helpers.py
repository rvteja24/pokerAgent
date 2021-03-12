import _pickle as pickle
import os
from InformationAbstracter import InformationAbstracter
class HelperClass:
    # to be used while updating trees after each game during training
    def __init__(self):
        self.information_abstracter = InformationAbstracter()
    @staticmethod
    def update_tree(tree, tree_name):
        with open(tree_name, 'wb') as file:
            file.write(pickle.dumps(tree))

    def tree_builder(self, valid_actions, hole_card, round_state):
        actionsTree, file_path = self.information_abstracter.get_tree_details(hole_card, round_state["street"])
        pathMapper = {"preflop" : "strategies/preflop", "flop" : "strategies/flop", "river" : "strategies/river", "turn" : "strategies/turn"}
        if round_state["street"] == "preflop":
            playerIdMap = {}
            for each in round_state["seats"]:
                playerIdMap[each["uuid"]] = each["name"]
            for each in round_state["action_histories"].items():
                # print(each[0])
                round = each[0]
                moves = each[1]
                if round == "preflop":
                    # print(each[1])
                    actionsTree = self.updateChildDicts(moves, playerIdMap, actionsTree)
                    self.update_tree(actionsTree, file_path)
                print(" --------- ", actionsTree)

    def updateChildDicts(self, moves, playerIdMap, actionTree):
        playerId = playerIdMap[moves[0]["uuid"]]
        moveId = moves[0]["action"] + "-" + str(moves[0]["amount"])
        if not actionTree.get(playerId):
            actionTree[playerId] = {}
        if moveId in actionTree[playerId]:
            del moves[0]
            if len(moves) > 0:
                actionTree[playerId][moveId] = self.updateChildDicts(moves, playerIdMap, actionTree[playerId][moveId])
        else:
            actionTree[playerId][moveId] = {}
            del moves[0]
            if len(moves) > 0:
                actionTree[playerId][moveId] = self.updateChildDicts(moves, playerIdMap, actionTree[playerId][moveId])
        return actionTree
