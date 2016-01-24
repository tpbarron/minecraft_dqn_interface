import Action
import random
import os
from game_globals import *

##############################
# Frequently Changed Globals #
##############################

# The width and height of the viewable game window (always square)
# For maximum speed, set this to 84 to match the scaled size (no scaling is required!)
TEST_WINDOW_SIZE = 600
TRAIN_WINDOW_SIZE = 84

# The width and height of the image sent to DeepMind
#SCALED_WINDOW_SIZE = 84

TICKS_PER_SEC = 6000

# Total number of game frames per episode
MAXIMUM_GAME_FRAMES = 500

# Agent's turning speed (per tick)
AGENT_ROTATION_SPEED = 1.50
WALKING_SPEED = 1.0

# World generation parameters
WORLD_WIDTH = 5  # width in both directions from start
WORLD_DEPTH = 5  # depth in both directions from start
NUMBER_GRASS_BLOCKS = 8  # number of dirt blocks to add randomly through world
NUMBER_BRICK_BLOCKS = 7 # number of brick blocks to add randomly through world
MAX_BLOCK_HEIGHT = 5 # The maximum height of blocks placed in the world

# How often to print out the total number of frames 
#COUNTER_DISPLAY_FREQUENCY = 1000

# GPU Training, -1 is CPU and 0 is GPU
#GPU = 0

##############
# Game rules #
##############
# Rewards and penalties must fit into one byte!
# All accumulated rewards also must be non-negative!!!
# Rewards (these are added to reward)

# How much do you get for breaking different blocks?
BLOCK_BREAK_REWARDS = {
    "GRASS":1,
    "STONE":0,
    "BRICK":0
}

# Penalties (these are subtracted from reward)
SWING_PENALTY = 0
EXISTENCE_PENALTY = 0

# If you get all the penalties, then you get zero
STARTING_REWARD = SWING_PENALTY + EXISTENCE_PENALTY

#################################################
# Game Actions 
#
# The interface using the legal action list for training. Define your actions 
# below and update the legal actions array to define which ones are valid
################################################
LEGAL_ACTIONS = [0, 1, 2, 3, 4, 5, 6]

GAME_ACTIONS = [
    #  (break_block, updown_rot, leftright_rot, forwardback, leftright)
    
    #0  Do nothing
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=0),

    #1  Go forward
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=WALKING_SPEED, leftright=0),
    
    #2  Go backward
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=-WALKING_SPEED, leftright=0),
    
    #3  Rotate right
    Action.Action(False, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=0, leftright=0),
    
    #-4  Rotate right and go forward
    #Action.Action(False, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=1, leftright=0),
    
    #-5  Rotate right and go backward
    #Action.Action(False, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=-1, leftright=0),
    
    #4  Rotate left
    Action.Action(False, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=0, leftright=0),

    #-7  Rotate left and go forward
    #Action.Action(False, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=1, leftright=0),
    
    #-8  Rotate left and go backward
    #Action.Action(False, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=-1, leftright=0),
        
    #-9 Click
    #Action.Action(True, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=0),
    
    #10 Click and go forward
    #Action.Action(True, updown_rot=0.0, leftright_rot=0.0, forwardback=1, leftright=0),
    
    #11 Click and go backward
    #Action.Action(True, updown_rot=0.0, leftright_rot=0.0, forwardback=-1, leftright=0),
    
    #12 Click and rotate right
    #Action.Action(True, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=0, leftright=0),
    
    #13 Click and rotate right and go forward
    #Action.Action(True, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=1, leftright=0),
    
    #14 Click and rotate right and go backward
    #Action.Action(True, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=-1, leftright=0),

    #15 Click and rotate left
    #Action.Action(True, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=0, leftright=0),
    
    #16 Click and rotate left and go forward
    #Action.Action(True, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=1, leftright=0),

    #17 Click and rotate left and go backward
    #Action.Action(True, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=-1, leftright=0),

    #18 Go right
    #Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=WALKING_SPEED),
    
    #19 Go left
    #Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=-WALKING_SPEED),

    #5 Rotate up
    Action.Action(False, updown_rot=AGENT_ROTATION_SPEED, leftright_rot=0.0, forwardback=0, leftright=0),
    
    #6 Rotate down
    Action.Action(False, updown_rot=-AGENT_ROTATION_SPEED, leftright_rot=0.0, forwardback=0, leftright=0)
]


###############
# Build World #
###############
GROUND = -2
WALL_HEIGHT = 2

def saveWorld(locations, filename):
    o = open(MAPS_PATH + os.sep + filename, 'w')
    for location in locations:
        o.write("%d %d %d %s\n" % location)
    o.close()
    
def generateTower(locations, texture):
    randomX = random.randrange(-WORLD_WIDTH+1, WORLD_WIDTH-1)
    randomZ = random.randrange(-WORLD_DEPTH+1, WORLD_DEPTH-1)
    # Don't make it the ground or the agent could fall through if it breaks it...
    randomY = GROUND + 1 + random.randrange(MAX_BLOCK_HEIGHT)
    
    locations.append((randomX, randomY, randomZ, texture))
    
    return locations
    

def generateFlatWorld(locations):
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


def generateWalkwayWorld(locations):    
    # a block to start on
    locations.append((0, GROUND, 0, "STONE"))
  
    # Make a snaking walkway
    i = 0
    j = 0
    block_count = 0
    while block_count < 10:
        locations.append((i, GROUND, j, "STONE"))
        #if random.random() < 0.1:
        #    locations.append((i, GROUND+1, j, "GRASS"))
        new_i = random.randrange(i-1, i+2)
        if new_i != i:
            locations.append((new_i, GROUND, j, "STONE"))
        j = j-1           
        i = new_i
        block_count += 1

    return locations
    
    
def generateShortEasyWalkwayWorld(locations):    
    # a block to start on
    locations.append((0, GROUND, 0, "STONE"))
    for i in range(100):
        locations.append((0, GROUND, -i, "STONE"))

    return locations

#####################################
# This function gets called mid game
# Implement it to define your task
#####################################
def generateGameWorld(filename):
    locs = []
    locs = generateWalkwayWorld(locs)
#    locs = generateFlatWorld(locs)
#    for i in range(NUMBER_GRASS_BLOCKS):
#        locs = generateTower(locs, "GRASS")
#    for i in range(NUMBER_BRICK_BLOCKS):
#        locs = generateTower(locs, "BRICK")
    saveWorld(locs, filename)

