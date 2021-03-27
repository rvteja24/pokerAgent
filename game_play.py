# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:39:51 2021

@author: vijaya_rayavarapu
"""

from basic_player import BasicPlayer
from agent import Agent
from basic_player import BasicPlayer
from rival_agent import DataBloggerBot

from pypokerengine.api.game import setup_config, start_poker
agent1 = Agent(name="p1")
agent2 = Agent(name="p2")
agent3 = Agent(name="p3")
agent4 = Agent(name="p4")
agent5 = Agent(name="p5")
agent6 = Agent(name="p6")
agents = [agent1, agent2, agent3, agent4, agent5, agent6]
players = ["p1","p2","p3","p4","p5","p6"]
for i in range(1,2):
    k = 0
    config = setup_config(max_round=200, initial_stack=10000, small_blind_amount=10)
    config.register_player(name=players[0-k], algorithm=agents[0-k])
    config.register_player(name=players[1-k], algorithm=agents[1-k])
    # config.register_player(name=players[2-k], algorithm=agents[2-k])
    config.register_player(name="p3", algorithm=BasicPlayer())
    config.register_player(name=players[3-k], algorithm=agents[3-k])
    # config.register_player(name=players[4-k], algorithm=agents[4-k])
    config.register_player(name="p5", algorithm=BasicPlayer())
    config.register_player(name=players[5-k], algorithm=agents[5-k])
    # config.register_player(name="p2", algorithm=BasicPlayer())

    # config.register_player(name="p4", algorithm=BasicPlayer())

    # config.register_player(name="p6", algorithm=BasicPlayer())
    game_result = start_poker(config, verbose=2)
    #print(game_result)
    # agent1.updateResult(game_result)
    # agent2.updateResult(game_result)
    # agent3.updateResult(game_result)
    # agent4.updateResult(game_result)
    # agent5.updateResult(game_result)
    # agent6.updateResult(game_result)
    if i%100 == 0:
        print(str(i) + " ----------------------------games done")
#print("final result here: ", game_result)
# import os
# os.system("shutdown /s /t 1")