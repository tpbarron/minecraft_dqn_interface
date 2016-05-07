import Action
import random
import os

#from game_globals import *
from tasks.Path_Creation import *

##############################
# Frequently Changed Globals #
##############################

# The width and height of the viewable game window (always square)
# For maximum speed, set this to 84 to match the scaled size (no scaling is required!)
TEST_WINDOW_SIZE = 84 # 600
TRAIN_WINDOW_SIZE = 84

ANIMATION_GENERATION = False

# The width and height of the image sent to DeepMind
#SCALED_WINDOW_SIZE = 84

TICKS_PER_SEC = 6000

# Total number of game frames per episode
# MOVED TO TASK!
#MAXIMUM_GAME_FRAMES = 2500

# Agent's turning speed (per tick)
# AGENT_ROTATION_SPEED = 1.50
# WALKING_SPEED = 1.0

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


#
# Tasks
#
TASK = Path_Creation()







