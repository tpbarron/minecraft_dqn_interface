"""
Walkway task specific code
"""

import random
import math

from Task import Task
from Walkway import Walkway
import game_config


class TinyWalkway(Task):

    def __init__(self):
        super(TinyWalkway, self).__init__()
        self.length = 2
        
    def generateGameWorld(self, filename):
        locs = []
        locs = self.generateWalkwayWorld(locs)
        self.saveWorld(locs, filename)
        
    def generateWalkwayWorld(self, locations):    
        # a block to start on
        locations.append((0, Task.GROUND, 0, "STONE"))
      
        # Make a snaking walkway
        i = 0
        j = 0
        block_count = 0
        while block_count < self.length:
            locations.append((i, Task.GROUND, j, "STONE"))
            #if random.random() < 0.1:
            #    locations.append((i, GROUND+1, j, "GRASS"))
            new_i = random.randrange(i-1, i+2)
            if new_i != i:
                locations.append((new_i, Task.GROUND, j, "STONE"))
            j = j-1           
            i = new_i
            block_count += 1

        return locations   

    
    def getReward(self, player):
        # Initialize a new reward for this current action
        reward = game_config.STARTING_REWARD

        try:
            dist = math.sqrt(player.position[0] ** 2 + player.position[2] ** 2)
            if dist > player.prev_max_distance:
                player.prev_max_distance = dist
                reward = 1
                #print player.prev_max_distance
        except AttributeError:
                #print 'Attribute error'
                player.prev_max_distance = 0

        if (player.position[1] < -1):
            reward = -1 #0 #-1         
        if (player.position[1] < -40):
            player.should_end_game = True
            player.prev_max_distance = 0

        #print ("Player reward = ", reward)
        return reward



