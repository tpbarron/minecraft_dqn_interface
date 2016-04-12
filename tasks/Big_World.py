"""
Walkway task specific code
"""

import random

from Task import Task
import game_config

class Big_World(Task):

    def __init__(self):
        super(Big_World, self).__init__()

    def generateGameWorld(self, filename):
        locs = []
        locs = self.generateBigWorld(locs)
        self.saveWorld(locs, filename)

    def generateBigWorld(self, locations):
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                locations.append((x, y - 2, z, "GRASS"))
                locations.append((x, y - 3, z, "STONE"))
                # self.add_block((x, y - 2, z), GRASS, immediate=False)
                # self.add_block((x, y - 3, z), STONE, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        locations.append((x, y + dy, z, "STONE"))
                        # self.add_block((x, y + dy, z), STONE, immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in xrange(75):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(2, 8) #6) # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["GRASS", "SAND", "BRICK"])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        #self.add_block((x, y, z), t, immediate=False)
                        locations.append((x, y, z, t))
                s -= d  # decrement side lenth so hills taper off
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
        if (player.position[1] > player.prev_max_y):
          player.prev_max_y = player.position[1]
          reward = 1.0
        elif (player.position[1] > player.prev_max_y):
          reward = -1.0

        #print ("Player reward = ", reward)
        return reward
