import InformationAbstracter as ia
import ActionAbstracter as aa
#
# abstracter = ia.InformationAbstracter()
# k = aa.ActionAbstracter()
# print(k.get_mappable_raise_value(8320))
# a = abstracter.get_tree_details(["5H", "3S"])
# print(a)
#
# brightness_4
# importing the module
import pickle
#
# # opening file in write mode (binary)
# file = open("strategies/trashTrees/trashTree52.txt", "wb")
#
# my_dict = []
#
# # serializing dictionary
# pickle.dump(my_dict, file)

with open("strategies/preflop/trashTrees/trashTree98p" + "4" +".txt", "rb") as file:
    print(pickle.loads(file.read()))
import re

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
