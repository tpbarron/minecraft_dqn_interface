"""
Path Creation task specific code
"""

import random
from collections import deque
from Task import Task
import game_config

class Dangerous_Walkway(Task):
    def __init__(self):
        self.complexity = 0
        self.max_complexity = 4
        self.average_number = 10
        self.previous_scores = deque([], self.average_number)
        self.path_length = 500
        # Level up when passed 20% of path distance
        self.level_up_score = self.path_length / 10 * 4
        self.game_ticks = 0
        self.previous_ticks = -50
        # Set to 3 with four frames of input
        self.wait_ticks = 3
        
    def generateGameWorld(self, filename):
        locs = []
        locs = self.generatePathWorld(locs)
        self.saveWorld(locs, filename)

    def generatePathWorld(self, locations):
        # a block to start on
        path_width = 5 - self.complexity
        # a block to start on
        locations.append((0, Task.GROUND, 0, "STONE"))

        # Make a snaking walkway
        i = 0
        j = 0
        block_count = 0
        while block_count < self.path_length:
            locations.append((i, Task.GROUND, j, "STONE"))
            new_i = random.randrange(i-1, i+2) #random.choice([i-1, i+1]) #
            for k in xrange(path_width):
                # -2 to move have agent in center
                if new_i+k-path_width/2 != i:
                    locations.append((new_i+k-(path_width/2), Task.GROUND, j, "STONE"))
            j = j-1
            i = new_i
            block_count += 1

        return locations
        
    def getReward(self, player):
        # Perform click actions
        # self.game_ticks += 1
        # act = player.actions[actionIndex]
        # if act.create_block and self.game_ticks > self.previous_ticks:
        #     self.previous_ticks = self.game_ticks + self.wait_ticks
        #     player.simulate_right_click()
        # if act.break_block and self.game_ticks > self.previous_ticks:
        #     self.previous_ticks = self.game_ticks + self.wait_ticks
        #     player.simulate_click()
        
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
            reward = 0
        if (player.position[1] < -1):
            reward = -1
        if (player.position[1] < -400):
          # the player fell, end the game early
            player.should_end_game = True

        #print ("Player reward = ", reward)
        return reward

    def reset(self, game_counter, game_score):
        # Use a moving average of the previous 500 games played
        self.previous_scores.append(game_score)
        # Every average_number of games check if the player has the minimal average score to level up
        average = sum(self.previous_scores) / self.average_number
        print self.average_number,  "Game Average:", average, "Current Complexity:", self.complexity
        if len(self.previous_scores) == self.average_number and self.complexity < self.max_complexity:
            if average >= self.level_up_score:
                self.complexity += 1
                print "INCREASED COMPLEXITY TO:", self.complexity
                # If it ever creates a path, then let it level up by not changing level up score.
                #self.level_up_score = self.gap * 4 + (self.complexity + 1) * 4
#                game_config.MAXIMUM_GAME_FRAMES = 640 + self.complexity * 320
                # Remove all previous scores after complexity increases
                self.previous_scores.clear()
        return self.complexity

if __name__ == "__main__":
    pc = Path_Creation()
    pc.generateGameWorld("test.txt")
    print pc.level_up_score
