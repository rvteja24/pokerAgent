import InformationAbstracter as ia
import ActionAbstracter as aa
#
# abstracter = ia.InformationAbstracter()
k = aa.ActionAbstracter()
# print(k.get_mappable_raise_value(5000, 330, 'preflop', 8200))
# print(k.get_abstracted_raise_values(768,'flop', 9030, 5000))
# print(k.get_abstracted_raise_values(575,'turn', 9800, 700))
# print(k.get_abstracted_raise_values(350,'river', 9910, 1100))
# print(tuple((tuple(["a","b","e", "f"]),tuple(["c", "d"]))))
# a = abstracter.get_tree_details(["5H", "3S"])
# print(a)
# a = [1,2,3,4,5]
#
# for i in range(20):
#     k = i%6
#     print(a[0-k])
#     print(a[1 - k])
#     print(a[2 - k])
#     print(a[3 - k])
#     print(a[4 - k])
# brightness_4
# importing the module
import pickle
#
# # opening file in write mode (binary)
# file = open("treeDicts/restTreesDict.txt", "wb")
#
# my_dict = {}

# serializing dictionary
# pickle.dump(my_dict, file)
# for i in range(2,3):
#     with open("strategies/preflop/pairsTrees/pairsTree"+str(i)+"p" + "2" +".txt", "rb") as file:
#         print(pickle.loads(file.read()))
# import re
with open("strategies/preflop/restTrees/TreeJAp" + "3" +".txt", "rb") as file:
    a = (pickle.loads(file.read()))
    print(a)
#
# import os
# trees = []
# a = os.listdir("C:\\Users\\rvtej\\Documents\\Spring 2021\\FAI\\pokerAgent\\strategies\\preflop\\restTrees")
# for each in a:
#     if each[3:6] not in trees:
#         trees.append(each[3:6])
# print(trees)
# with open("treeDicts/restTreesDict.txt", "rb") as file:
#     print(format(pickle.loads(file.read())))
# print(str("apple"))
# c = ('5H','3S','2D','3D','8C')
# #
# k = {('5H','2D','3D','8C','3S'): "Correct", ('5D','2D','3D','3C','3S'): "incorrect" }
# #
#
# for i in k.items():
#     if set(c) == set(i[0]):
#         print("YAyy")
# a = [1,2,3]
# b = [1,2]
#
# d = tuple(a+b)
# print(d)
# expl = "CALL"
#
# expl = expl.split("-")
# val = expl[1] if len(expl) == 2 else 0
# print(val)
# actionTuple = {("r", "300"):(0,0), ("c", "0"):(1,-10), ("r", "500"):(2,20), ("f", "0"):(0,0)}
# # best_move = min(actionTuple.items(), key=lambda x: x[1][0])[0]
# # print(best_move)
# import random
# print(random.choice(list(filter(lambda x: x[1][0] == 0, actionTuple.items()))))
from matplotlib import pyplot as plt
from treys import Evaluator
from treys import Card as card
# evaluator = Evaluator()
# cards = []
# suits = ["h", "d", "c", "s"]
# vals = ["A","J", "Q", "K", "T", "2", "3", "4", "5", "6", "7", "8", "9"]
# evals = []
#
# for e in vals:
#     for j in suits:
#         cards.append(e+j)
# # print((cards))
#
# cards1 = []
# for e in vals:
#     for j in suits:
#         cards1.append((j+e).upper())
# #
# print(cards1)
# cardMapDict = {}
# # # for i, carda in enumerate(cards1):
# # #     cardMapDict[carda] = cards[i]
# with open("treeDicts/TreesDict.txt", 'wb') as file:
#     file.write(pickle.dumps(cardMapDict))
#
# tree = {}
# with open("cardMap.dict", "rb") as file:
#     tree = pickle.loads(file.read())
#
# print(tree)
# for k in cards:
#     t = cards
#     t.remove(k)
#     for j in t:
#         q = t
#         q.remove(j)
#         for e in q:
#             a = q
#             a.remove(e)
#             for l in a:
#                 b = a
#                 b.remove(l)
#                 for m in b:
#                     n = b
#                     n.remove(m)
#                     for w in n:
#                         p = n
#                         p.remove(w)
#                         for u in p:
#                             board = [
#                                 card.new(k),
#                                 card.new(j),
#                                 card.new(e),
#                                 card.new(l),
#                                 card.new(m)
#                             ]
#                             hand = [card.new(w), card.new(u)]
#                             evals.append(evaluator.evaluate(hand, board))
#
# len(evals)
#
# plt.plot(evals)

# board = [
#     card.new('2h'),
#      card.new('5d'),
#      card.new('Jc')
# ]
# hand = [card.new('8s'), card.new("".join(list('TH')[0] + list('TH')[1].lower()))]
# print(evaluator.evaluate(hand, board))
# a ={1:(2,3)}
#
# a[1] = (4,5)
# print(a)