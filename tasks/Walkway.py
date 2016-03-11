"""
Walkway task specific code
"""

import random

from Task import Task
import game_config

class Walkway(Task):

    def __init__(self):
        super(Walkway, self).__init__()
        self.length = 10
        
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
        
        
    def generateShortEasyWalkwayWorld(self, locations):    
        # a block to start on
        locations.append((0, Task.GROUND, 0, "STONE"))
        for i in range(self.length):
            locations.append((0, Task.GROUND, -i, "STONE"))

        return locations
    
    
    def getReward(self, player):
        #print ("Player get reward")
        # Initialize a new reward for this current action
        reward = game_config.STARTING_REWARD
            
        # Each part of the action might have a cost or reward
        # E.g. Moving might have an energy cost
        # E.g. Breaking blocks might be good or bad; reward or penalty
        
        # Check if farther than before. Then give reward.
        # Going away in the z dir is negative.
        # by rounding, the max score should be the z dist of the path
        #print (self.position)
        if (player.position[2] < player.prev_max_z):
          player.prev_max_z = player.position[2]
          reward = 1.0
        elif (player.position[2] > player.prev_max_z):
          reward = -1.0

        if (player.position[1] < -1):
          # the player fell, end the game early
          player.should_end_game = True
          reward = 0.0 #-1

        #print ("Player reward = ", reward)
        return reward

