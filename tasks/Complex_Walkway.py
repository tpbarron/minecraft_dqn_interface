"""
Complex Walkway task specific code
"""

import random
from collections import deque
from Task import Task
import game_config

class Complex_Walkway(Task):
    def __init__(self):
        self.complexity = 0
        self.average_number = 250
        self.previous_scores = deque([], self.average_number)
        self.level_up_score = 50
    
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
        while j > -40:
            connectors = random.randint(1, 4)
            for connections in xrange(connectors):
                locations.append((i, Task.GROUND, j, "STONE"))
                j = j - 1
            locations.append((i, Task.GROUND, j, "STONE"))
            direction = 1 if random.random() > .5 else -1
            for path_length in xrange(random.randint(0, self.complexity)):
                i += direction
                locations.append((i, Task.GROUND, j, "STONE"))            
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
          reward = 1
        elif (player.position[2] > player.prev_max_z):
          reward = -1

        if (player.position[1] < -1):
          # the player fell, end the game early
          player.should_end_game = True
          reward = 0 #-1

        #print ("Player reward = ", reward)
        return reward

    def reset(self, game_counter, game_score):
        # Use a moving average of the previous 500 games played
        self.previous_scores.append(game_score)
        # Every average_number of games check if the player has the minimal average score to level up
        if len(self.previous_scores) == self.average_number:
            average = sum(self.previous_scores) / self.average_number
            print self.average_number,  "Game average:", average
            if average >= self.level_up_score:
                self.complexity += 1
                print "Increased complexity to:", self.complexity
                game_config.MAXIMUM_GAME_FRAMES = 640 + self.complexity * 320
        return self.complexity
