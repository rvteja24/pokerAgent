# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:39:51 2021

@author: vijaya_rayavarapu
"""

from rival_agent_garb import TrainedPlayer as T2
from rival_agent_trained import TrainedPlayer as T1
from tree_search import HonestPlayer
from agent import Agent
from rival_agent_caller import BasicPlayer
from rival_agent_mcts import DataBloggerBot

from pypokerengine.api.game import setup_config, start_poker
agent1 = Agent(name="p1")
agent2 = Agent(name="p2")
agent3 = Agent(name="p3")
agent4 = Agent(name="p4")
agent5 = Agent(name="p5")
agent6 = Agent(name="p6")
agents = [agent1, agent2, agent3, agent4, agent5, agent6]
players = ["p1","p2","p3","p4","p5","p6"]
profits = {"p1": 0, "p2": 0, "p3": 0,"p4": 0, "p5": 0, "p6": 0}
n = 100
for i in range(0, n):
    k = 0
    config = setup_config(max_round=10, initial_stack=10000, small_blind_amount=10)
    # config.register_player(name=players[0-k], algorithm=agents[0-k])
    # config.register_player(name=players[1-k], algorithm=agents[1-k])
    # config.register_player(name=players[2-k], algorithm=agents[2-k])
    # config.register_player(name=players[3-k], algorithm=agents[3-k])
    # config.register_player(name=players[4-k], algorithm=agents[4-k])
    # config.register_player(name=players[5-k], algorithm=agents[5-k])
    config.register_player(name=players[0-k], algorithm=agents[0-k])
    config.register_player(name=players[1-k], algorithm=agents[1-k])
    config.register_player(name=players[2-k], algorithm=agents[2-k])
    config.register_player(name=players[3-k], algorithm=agents[3-k])
    config.register_player(name=players[4-k], algorithm=agents[4-k])
    config.register_player(name=players[5-k], algorithm=agents[5-k])
    game_result = start_poker(config, verbose=0)

    # winner = max(game_result['players'], key= lambda x: x['stack'])["name"]
    # results = "Game " + str(i) + ": \n"
    for each in game_result['players']:
        profits[each["name"]] += each["stack"]
    #     if players[1-k] == each["name"] or players[3-k] == each["name"] or players[4-k] == each["name"]: # or  players[3-k] == each["name"]: # or  players[3-k] == each["name"]:
    #         if winner == each["name"]:
    #             results += "Winner Rival Agent" + each['name'] + ': ' + str(each['stack']) + '\n'
    #         else:
    #             results += "Rival Agent" + each['name'] + ': ' + str(each['stack']) + '\n'
    #     else:
    #         if winner == each['name']:
    #             results += "Winner SAge" + each['name'] + ': ' + str(each['stack']) + '\n'
    #         else:
    #             results += "SAge" + each['name'] + ': ' + str(each['stack']) + '\n'
    # results += "Winner is: " + winner + '\n\n'
    with open("tests/v2_v1_2.txt", "a") as f:
        f.write(str(profits) + "\n")
        f.close()
    # for each in agents:
    #     each.updateResult(game_result)
    # agent1.updateResult(game_result)
    # agent2.updateResult(game_result)
    # agent3.updateResult(game_result)
    # agent4.updateResult(game_result)
    # agent5.updateResult(game_result)
    # agent6.updateResult(game_result)
    if i%100 == 0:
        print(str(i) + " ----------------------------games done\n\n")
for each in profits.items():
    profits[each[0]] = each[1]/n
print(profits)
# with open("tests/test_10000_3_6_rivals_games_after450000.txt", "a") as f:
#     f.write("Net profits: " + str(profits))
#     f.close()
#print("final result here: ", game_result)
# import os
# os.system("shutdown /s /t 1")