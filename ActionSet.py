import Action
#import game_config

#
# Game Actions
#
# The interface using the legal action list for training. Define your actions
# below and update the legal actions array to define which ones are valid
#


# Agent's turning speed (per tick)
AGENT_ROTATION_SPEED = 1.50
WALKING_SPEED = 1.0


#LEGAL_ACTIONS = [0, 1, 2, 3, 4, 5, 6]

DO_NOTHING = 0
GO_FORWARD = 1
GO_BACKWARD = 2 
GO_RIGHT = 3
GO_LEFT = 4
ROTATE_RIGHT = 5
ROTATE_LEFT = 6
ROTATE_UP = 7
ROTATE_DOWN = 8
REMOVE_BLOCK = 9
CREATE_BLOCK = 10
JUMP = 11

#print dir(game_config)

GAME_ACTIONS = [

    #0  Do nothing
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=0, jump=False, create_block=False),

    #1  Go forward
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=-WALKING_SPEED, leftright=0, jump=False, create_block=False),

    #2  Go backward
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=WALKING_SPEED, leftright=0, jump=False, create_block=False),

    #3 Go right
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=WALKING_SPEED, jump=False, create_block=False),

    #4 Go left
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=-WALKING_SPEED, jump=False, create_block=False),

    #5  Rotate right
    Action.Action(False, updown_rot=0.0, leftright_rot=AGENT_ROTATION_SPEED, forwardback=0, leftright=0, jump=False, create_block=False),

    #6  Rotate left
    Action.Action(False, updown_rot=0.0, leftright_rot=-AGENT_ROTATION_SPEED, forwardback=0, leftright=0, jump=False, create_block=False),

    #7 Rotate up
    Action.Action(False, updown_rot=AGENT_ROTATION_SPEED, leftright_rot=0.0, forwardback=0, leftright=0, jump=False, create_block=False),

    #8 Rotate down
    Action.Action(False, updown_rot=-AGENT_ROTATION_SPEED, leftright_rot=0.0, forwardback=0, leftright=0, jump=False, create_block=False),

    #9 Remove block
    Action.Action(True, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=0, jump=False, create_block=False),

    #10 Place block
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=0, leftright=0, jump=False, create_block=True),

    #11 Jump forward
    Action.Action(False, updown_rot=0.0, leftright_rot=0.0, forwardback=-WALKING_SPEED, leftright=0, jump=True, create_block=False)





]
