# -*- coding: utf-8 -*-
"""
Created on Sun March 7
"""
import _pickle as pickle
import os


class InformationAbstracter:
    # Fetches dicts for pairs, sameSuit and trash which has key as the card and value as the file where tree is stored.
    def __init__(self):
        with open("treeDicts/pairsTreesDict.txt", 'rb') as file:
            self.pairsTreeDict = pickle.loads(file.read())
            file.close()
        # with open("treeDicts/sameSuitTreeDict.txt", 'rb') as file:
        #     self.sameSuitTreeDict = pickle.loads(file.read())
        #     file.close()
        with open("treeDicts/restTreesDict.txt", 'rb') as file:
            self.trashTreeDict = pickle.loads(file.read())
            file.close()

    # we are just getting the path to the file where tree is stored, this way we can reduce the size and searching
    # required to get just one tree.
    def get_tree_name(self, cardPair, round, small_blind):
        card1 = cardPair[0][::-1]
        card2 = cardPair[1][::-1]
        if card1[0] == card2[0]:
            if card1[0] + small_blind in self.pairsTreeDict.keys():
                return self.pairsTreeDict.get(card1[0] + small_blind)
            else:
                self.pairsTreeDict[card1[0] + small_blind] = "strategies/"+round+"/pairsTrees/pairsTree" + card1[0] + small_blind +".txt"
                with open("treeDicts/pairsTreesDict.txt", 'wb') as file:
                    file.write(pickle.dumps(self.pairsTreeDict))
                return "strategies/"+round+"/pairsTrees/pairsTree" + card1[0] + small_blind +".txt"
        # elif card1[0] != card2[0] and card1[1] == card2[1]:
        #     if ((card1[0], card2[0]), small_blind) in self.sameSuitTreeDict.keys():
        #         return self.sameSuitTreeDict.get(((card1[0], card2[0]), small_blind))
        #     elif ((card2[0], card1[0]), small_blind) in self.sameSuitTreeDict.keys():
        #         return self.sameSuitTreeDict.get(((card2[0], card1[0]), small_blind))
        #     else:
        #         self.sameSuitTreeDict[((card1[0], card2[0]), small_blind)] = "strategies/"+round+"/sameSuitTrees/sameSuitTree" + card1[0] + \
        #                                                       card2[0] +  small_blind + ".txt"
        #         with open('treeDicts/sameSuitTreeDict.txt', 'wb') as file:
        #             file.write(pickle.dumps(self.sameSuitTreeDict))
        #         return "strategies/"+round+"/sameSuitTrees/sameSuitTree" + card1[0] + card2[0] +  small_blind + ".txt"
        else:
            if ((card1[0], card2[0]), small_blind) in self.trashTreeDict.keys():
                return self.trashTreeDict.get(((card1[0], card2[0]), small_blind))
            elif ((card2[0], card1[0]), small_blind) in self.trashTreeDict.keys():
                return self.trashTreeDict.get(((card2[0], card1[0]), small_blind))
            else:
                self.trashTreeDict[((card1[0], card2[0]), small_blind)] = "strategies/"+round+"/restTrees/Tree" + card1[0] + card2[
                    0] +  small_blind  +".txt"
                with open("treeDicts/restTreesDict.txt", 'wb') as file:
                    file.write(pickle.dumps(self.trashTreeDict))
                return "strategies/"+round+"/restTrees/Tree" + card1[0] + card2[0] +  small_blind  +".txt"

    # with the tree name the tree is read and returned
    def get_tree_details(self, cardPair, round, small_blind):
        tree_name = self.get_tree_name(cardPair, round, small_blind)
        tree = {}
        if os.path.isfile(tree_name):
            with open(tree_name, "rb") as file:
                tree = pickle.loads(file.read())
        else:
            file = open(tree_name, "wb")
            tree = {}
            pickle.dump(tree, file)
        return tree, tree_name

