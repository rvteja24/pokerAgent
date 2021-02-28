# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 00:39:51 2021

@author: vijaya_rayavarapu
"""

from basic_player import BasicPlayer
from human_player import HumanPlayer
from pypokerengine.api.game import setup_config, start_poker

config = setup_config(max_round=1, initial_stack=100, small_blind_amount=5)
config.register_player(name="p1", algorithm=BasicPlayer())
config.register_player(name="p2", algorithm=BasicPlayer())
config.register_player(name="p3", algorithm=BasicPlayer())
config.register_player(name="p3", algorithm=HumanPlayer())
game_result = start_poker(config, verbose=1)