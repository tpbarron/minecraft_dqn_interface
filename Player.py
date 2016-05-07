import time
import pyglet
import math
import random

import Action

# from tasks.Task import Task
# from tasks.Walkway import Walkway
# from tasks.Complex_Walkway import Complex_Walkway
# from tasks.Big_World import Big_World
# from tasks.Dangerous_Walkway import Dangerous_Walkway
# from tasks.TinyWalkway import TinyWalkway
# from tasks.Path_Creation import Path_Creation

import game_config
import game_globals
import ActionSet

class Player(object):

    def __init__(self):

        # A list of blocks the player can place. Hit num keys to cycle.
        #self.inventory = [BRICK, GRASS, SAND]
        self.game = None

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Looking up/down or left/right?
        self.looking = [0, 0]

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        self.jump = False

        self.dy = 0

        # A list of blocks the player can place. Hit num keys to cycle.
        #self.inventory = [BRICK, GRASS, SAND]

        # The current block the user can place. Hit num keys to cycle.
        #self.block = self.inventory[0]

        #self.previous_reward = 0

        self.total_score = 0

        self.prev_max_z = 0
        self.prev_max_y = 0
        self.should_end_game = False

        self.actions = ActionSet.GAME_ACTIONS

        self.task = game_config.TASK   

        assert game_config.STARTING_REWARD >= game_config.EXISTENCE_PENALTY + game_config.SWING_PENALTY, "Penalties too high!"

    def reset(self):
        # A list of blocks the player can place. Hit num keys to cycle.
        #self.inventory = [BRICK, GRASS, SAND]
        self.game = None

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Looking up/down or left/right?
        self.looking = [0, 0]

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        self.jump = False

        self.dy = 0

        self.total_score = 0

        self.prev_max_z = 0
        self.prev_max_y = 0
        self.should_end_game = False

        self.actions = ActionSet.GAME_ACTIONS #game_config.GAME_ACTIONS

        # Set when initialized...no need to reset
        #self.task = self.createTask()

        assert game_config.STARTING_REWARD >= game_config.EXISTENCE_PENALTY + game_config.SWING_PENALTY, "Penalties too high!" 

    def endGameEarly(self):
        return self.should_end_game

    def setGame(self, game):
        self.game = game


    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def canJump(self):
        height = game_globals.PLAYER_HEIGHT
        pad = 0.25
        p = list(self.position)
        np = game_globals.normalize(self.position)
        for face in game_globals.FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.game.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        return True
                    break
        return False


    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """

        self.simulate_look(0, 0, self.looking[0], self.looking[1])

        if self.jump and self.canJump():
            self.jump = False
            self.dy = game_globals.JUMP_SPEED

        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def get_foot_position(self):
        return int(self.position[0]), int(self.position[1]-1), int(self.position[2])

    def get_head_position(self):
        return int(self.position[0]), int(self.position[1]-1)+1, int(self.position[2])

    #def on_mouse_motion(self, x, y, dx, dy):
    def simulate_look(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        m = 0.15
        x, y = self.rotation
        x, y = x + dx * m, y + -dy * m
        y = max(-90, min(90, y))
        self.rotation = (x, y)



    def simulate_click(self):
        vector = self.get_sight_vector()
        block, previous = self.game.model.hit_test(self.position, vector)
        #self.game.add_block(previous, self.block)
        if block:
            texture = self.game.model.world[block]
            if texture == game_globals.GRASS:
                #print "REMOVING BLOCK"
                self.game.model.try_remove_block(block)
                return "GRASS"
            elif texture == game_globals.STONE:
                return "STONE"
            elif texture == game_globals.BRICK:
                self.game.model.try_remove_block(block)
                return "BRICK"
            elif texture == game_globals.SAND:
                self.game.model.try_remove_block(block)
                return "SAND"
        else:
            return ""


    def simulate_right_click(self):
        vector = self.get_sight_vector()
        block, previous = self.game.model.hit_test(self.position, vector)
        if previous:
            self.game.model.add_block(previous)


    def performAction(self, actionIndex):
        """
        Perform an action by setting the agent's movement fields to the values from the action object
        NOTE: the break block action should be handled in the getReward method
        """
        act = self.actions[actionIndex]
        #print "ACTION: ", act

        #print ("Player perform action")
        self.strafe[0] = act.forwardbackward_walk
        self.strafe[1] = act.leftright_walk

        self.looking[0] = act.leftright_rotation
        self.looking[1] = act.updown_rotation

        self.jump = act.jump


    def getReward(self, actionIndex):
        #print ("DeepMindPlayer doAction: ", actionIndex)
        #act = self.actions[actionIndex]
        # carry out the action
        r = self.task.getReward(self, actionIndex)
        self.total_score += r
        return r
