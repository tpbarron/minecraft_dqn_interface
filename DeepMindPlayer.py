import time
import pyglet
import math
import random

import game_config

import Action
from Player import Player

class DeepMindPlayer(Player):

    def __init__(self, agent_filename=""):
        Player.__init__(self)
        self.actions = game_config.GAME_ACTIONS


    def performAction(self, actionIndex):
        #print ("DeepMindPlayer doAction: ", actionIndex)
        act = self.actions[actionIndex]
        # carry out the action
        return self.performActionPlayer(act)   
    
    def getReward(self, actionIndex):      
        #print ("DeepMindPlayer doAction: ", actionIndex)
        act = self.actions[actionIndex]
        # carry out the action
        return self.getRewardPlayer(act)   




