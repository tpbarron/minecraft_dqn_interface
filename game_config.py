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

ANIMATION_GENERATION = True

# The width and height of the image sent to DeepMind
#SCALED_WINDOW_SIZE = 84

TICKS_PER_SEC = 6000

# Total number of game frames per episode
MAXIMUM_GAME_FRAMES = 500

# Agent's turning speed (per tick)
AGENT_ROTATION_SPEED = 1.50
WALKING_SPEED = 1.0

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
WALKWAY = 0
BIG_WORLD = 1
COMPLEX_WALKWAY = 2

TASK = COMPLEX_WALKWAY

#
# Game Actions 
#
# The interface using the legal action list for training. Define your actions 
# below and update the legal actions array to define which ones are valid
#

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
