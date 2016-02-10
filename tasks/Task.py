
import os

import game_globals

class Task(object):

    # Default world generation parameters
    GROUND = -2
    WALL_HEIGHT = 2
    
    #WORLD_WIDTH = 5  # width in both directions from start
    #WORLD_DEPTH = 5  # depth in both directions from start
    #NUMBER_GRASS_BLOCKS = 8  # number of dirt blocks to add randomly through world
    #NUMBER_BRICK_BLOCKS = 7 # number of brick blocks to add randomly through world
    #MAX_BLOCK_HEIGHT = 5 # The maximum height of blocks placed in the world

    
    def __init__(self):
        pass
        
    def saveWorld(self, locations, filename):
        o = open(game_globals.MAPS_PATH + os.sep + filename, 'w')
        for location in locations:
            o.write("%d %d %d %s\n" % location)
        o.close()
        
    def generateTower(self, locations, texture):
        randomX = random.randrange(-WORLD_WIDTH+1, WORLD_WIDTH-1)
        randomZ = random.randrange(-WORLD_DEPTH+1, WORLD_DEPTH-1)
        # Don't make it the ground or the agent could fall through if it breaks it...
        randomY = GROUND + 1 + random.randrange(MAX_BLOCK_HEIGHT)
        
        locations.append((randomX, randomY, randomZ, texture))
        
        return locations
        

    def generateFlatWorld(self, locations):
        # Make the flat ground
        for i in range(-WORLD_WIDTH, WORLD_WIDTH):
            for j in range(-WORLD_DEPTH, WORLD_DEPTH):
                locations.append((i, GROUND, j, "STONE"))

        # Put walls around the outside
        for i in range(-2, WALL_HEIGHT):
            for j in range(-WORLD_DEPTH, WORLD_DEPTH):
                locations.append((-WORLD_WIDTH, i, j, "STONE"))
                locations.append((WORLD_WIDTH, i, j, "STONE"))
            for j in range(-WORLD_WIDTH, WORLD_WIDTH):
                locations.append((j, i, -WORLD_DEPTH, "STONE"))
                locations.append((j, i, WORLD_DEPTH, "STONE"))
        return locations
        
    def generateGameWorld(self, filename):
        print ("Must specify subtask")
        


               
