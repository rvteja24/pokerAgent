# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:39:51 2021

@author: vijaya_rayavarapu
"""

from basic_player import BasicPlayer
from agent import Agent
from pypokerengine.api.game import setup_config, start_poker

config = setup_config(max_round=1, initial_stack=10000, small_blind_amount=10)
config.register_player(name="p1", algorithm=Agent())
config.register_player(name="p2", algorithm=BasicPlayer())
config.register_player(name="p3", algorithm=BasicPlayer())
config.register_player(name="p4", algorithm=BasicPlayer())
config.register_player(name="p5", algorithm=BasicPlayer())
config.register_player(name="p6", algorithm=BasicPlayer())
game_result = start_poker(config)
