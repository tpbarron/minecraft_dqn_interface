import os
import math
import random
import time

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from PIL import Image
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from game_globals import *
from game_config import *

from Player import Player
from DeepMindPlayer import DeepMindPlayer

# field of view
FOV = 65.0
FOV_PLAYER = 90.0


class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        #self._initialize()



    def loadMap(self, level):
        #f = open("world.txt", 'r')
        f = open(MAPS_PATH + '/' + level, 'r')
        for line in f:
            x, y, z, kind = line.split()
            x, y, z = float(x), float(y), float(z)
            if kind == "GRASS":
                self.add_block((x, y, z), GRASS, immediate=False)
            elif kind == "STONE":
                self.add_block((x, y, z), STONE, immediate=False)
            elif kind == "BRICK":
                self.add_block((x, y, z), BRICK, immediate=False)
            #self.add_block((x, y - 3, z), STONE, immediate=False)
                
        f.close()
       


    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture=GRASS, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def try_remove_block(self, position, immediate=True):
        if position in self.world:
            self.remove_block(position, immediate)
        

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()


    def saveWorld(self, filename="maps" + os.sep + "world.txt"):
        o = open(filename, 'w')
        for position in self.world.keys():
            if self.world[position] == GRASS:
                o.write(("%d %d %d" % position) + " %s\n" % "GRASS")
            elif self.world[position] == STONE:
                o.write(("%d %d %d" % position) + " %s\n" % "STONE")
        o.close()


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model()

        # Number of ticks gone by in the world
        self.world_counter = 0

        # The label that is displayed in the top left of the canvas.
        # self.label = pyglet.text.Label('', font_name='Arial', font_size=22, bold=True,
        #     x=20, y=self.height - 10, anchor_x='left', anchor_y='top', 
        #     color=(0,0,0,255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        #pyglet.clock.set_fps_limit(1000)
        #pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
        #pyglet.clock.schedule(self.update)

        #self.current_frame = [[.76, .67],[.88, .91]]
        
        # Int flag to indicate the end of the game
        # This is set to 1 whenever the max frames are reached
        # or the player dies
        self.game_over = False

        self.evaluate = False


    def reset(self):
        # Setup grayscale conversion color component scaling values
        glPixelTransferf(GL_RED_SCALE, 1)
        glPixelTransferf(GL_GREEN_SCALE, 1)
        glPixelTransferf(GL_BLUE_SCALE, 1)
    
        self.model = Model()
        self.world_counter = 0
        self.exclusive = False
        self.sector = None
        self.reticle = None
        self.game_over = False
        self.player = DeepMindPlayer()
        self.player.setGame(self)
        world_file = "test%d.txt" % random.randrange(10)
        generateGameWorld(world_file)
        self.model.loadMap(world_file)
        #self.set_game_frame_limit(10000) ??
        
        glPixelTransferf(GL_RED_SCALE, 0.299)
        glPixelTransferf(GL_GREEN_SCALE, 0.587)
        glPixelTransferf(GL_BLUE_SCALE, 0.114)
       

    def set_phase(self, evaluate):
        self.evaluate = evaluate

    def set_player(self, player):
        self.player = player
        
    def set_game_frame_limit(self, max_frames):
        self.max_frames = max_frames

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive


    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
     
        self.world_counter += 1
        if self.world_counter >= MAXIMUM_GAME_FRAMES:
            self.game_over = True
     
        self.model.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)
        

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if self.player.flying else WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.player.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.player.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.player.dy -= dt * GRAVITY
            self.player.dy = max(self.player.dy, -TERMINAL_VELOCITY)
            dy += self.player.dy * dt
        # collisions
        x, y, z = self.player.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.player.position = (x, y, z)


    def get_screen(self):
        """Get a screen shot of the current game state"""

        PIXEL_BYTE_SIZE = 1  # Use 1 for grayscale, 4 for RGBA
        # Initialize an array to store the screenshot pixels
        screenshot = (GLubyte * (PIXEL_BYTE_SIZE * self.width * self.height))(0)
        # Grab a screenshot
        # Use GL_RGB for color and GL_LUMINANCE for grayscale!
        #glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, screenshot)
        glReadPixels(0, 0, self.width, self.height, GL_LUMINANCE, GL_UNSIGNED_BYTE, screenshot)

        if (self.evaluate):
            # need to scale screen
            image = Image.fromstring(mode="L", size=(self.width, self.height),
                                     data=screenshot)
            image = image.resize((TRAIN_WINDOW_SIZE, TRAIN_WINDOW_SIZE))
            
            #image.save("frame.png")
            screenshot = image.getdata()
            #print (list(screenshot))
            #print (len(list(screenshot)))
            #image.show()
            #raw_input("Enter")

        return screenshot
        

<<<<<<< HEAD
    def get_faces(self, num=20):
        blocks = self.model.shown
        agentRot = self.player.rotation
        agentPos = self.player.position
        
        faces = []
        for blockPos in blocks.keys():
            # get all the vertices and determine if each face is visible
            blockVertices = cube_vertices(blockPos[0], blockPos[1], blockPos[2], 0.5)
            
            for v in range(0, len(blockVertices), 12):
                vertex0 = np.asarray((blockVertices[v],   blockVertices[v+1],  blockVertices[v+2]))
                vertex1 = np.asarray((blockVertices[v+3], blockVertices[v+4],  blockVertices[v+5]))
                vertex2 = np.asarray((blockVertices[v+6], blockVertices[v+7],  blockVertices[v+8]))
                vertex3 = np.asarray((blockVertices[v+9], blockVertices[v+10], blockVertices[v+11]))
                
                vector0 = vertex0 - vertex1
                vector1 = vertex0 - vertex2
                
                normal = np.cross(vector0, vector1)
                
                if (self.checkFace(normal, agentPos, agentRot)):    
                    faces.append(self.unit_vector(normal))
        
        print faces
            
    
    def checkFace(self, normal, agentPos, agentRot):
        yAxisRot = agentRot[0]
        xAxisRot = agentRot[1]
        
        # Translate normal vector to original coordinates
        # unrotate about y axis
        new_normal = self.rotateY(normal, math.radians(yAxisRot))
        
        # unrotate about x axis
        new_normal = self.rotateX(new_normal, math.radians(xAxisRot))
        
        # untranslate x, y, z
        new_normal = self.translate(new_normal, (-agentPos[0], -agentPos[1], -agentPos[2]))

        # check angle between normal and (0, 0, -1) sight vector
        angle = self.angle_between(new_normal, np.array(0, 0, -1))
        if (angle < np.pi / 2.0 or angle > 3 * np.pi / 2.0):
            return True
            
        return False
        
    
    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        angle = np.arccos(np.dot(v1_u, v2_u))
        if np.isnan(angle):
            if (v1_u == v2_u).all():
                return 0.0
            else:
                return np.pi
        return angle
    

    def get_volume(self, side=VOLUME_DIMENSION):
        # Alternative possibility
        # Rotate pos to block vector by -player rot
        # Sight vector will just be neg z

        blocks = self.model.shown
        
        agentRot = self.player.rotation
        agentPos = self.player.position
        
        volume = np.zeros((side, side, side))
        
        #points = []
        
        for blockPos in blocks.keys():
            # get vector from position to block
            # +1 on the y for eye height
            
            # check center 
            block_vec = (blockPos[0] - agentPos[0], blockPos[1] - (agentPos[1]), blockPos[2] - agentPos[2])
            offset = side / 10.0 / 2.0
            if (self.checkPoint(block_vec, agentPos, agentRot)):
                #points.append(block_vec)
                x, y, z = tuple([e*side/10.0 for e in block_vec])
                
                #print ("vol point = ", volPoint)
                # +49 since origin at center
                minx = int(round(x - offset + side/2.0 - 1))
                maxx = int(round(x + offset + side/2.0 - 1))
                
                miny = int(round(y - offset + side/2.0 - 1))
                maxy = int(round(y + offset + side/2.0 - 1))
                
                # flip z's into the positive side
                minz = -int(round(z + offset))
                maxz = -int(round(z - offset))
                
                #print ("bounds: ", minx, maxx, miny, maxy, minz, maxz)
                
                for xs in range(minx, maxx, 1):
                    for ys in range(miny, maxy, 1):
                        for zs in range(minz, maxz, 1):
                            if (xs >= 0 and xs < side):
                                if (ys >= 0 and ys < side):
                                    if (zs >= 0 and zs < side):
                                        #print ("adding point: ", (xs, ys, zs))
                                        #points.append((xs, ys, zs))
                                        volume[xs][ys][zs] = 1
                
                                 
            # check vertices            
            #blockVertices = cube_vertices(blockPos[0], blockPos[1], blockPos[2], 0.5)
            #for v in range(0, len(blockVertices), 3):
            #    vertex = (blockVertices[v], blockVertices[v+1], blockVertices[v+2])
            #    block_vec = (vertex[0] - agentPos[0], vertex[1] - (agentPos[1]), vertex[2] - agentPos[2])
                
            #    if (self.checkPoint(block_vec, agentPos, agentRot)):    
            #        points.append(block_vec)
                                
        #self.plot3d(points)
        
        return volume
    
    
    def plot3d(self, points, size=VOLUME_DIMENSION):
        fig = plt.figure()
        plt.ion()
        ax = fig.add_subplot(111, projection='3d')
        
        c = 'r'
        m = 'o'
        
        nPts = len(points)
        xs = np.zeros((nPts,))
        ys = np.zeros((nPts,))
        zs = np.zeros((nPts,))
        
        for i in range(nPts):
            xs[i] = points[i][0]
            ys[i] = points[i][1]
            zs[i] = points[i][2]
            
        ax.scatter(xs, ys, zs, c=c, marker=m)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        #ax.set_ylim([-(size/2-1),(size/2)])
        #ax.set_xlim([-(size/2-1),(size/2)])
        #ax.set_zlim([-size-1,0])

        ax.set_ylim([0, size-1])
        ax.set_xlim([0, size-1])
        ax.set_zlim([0, size-1])

        plt.show()
        raw_input("Enter: ")
        plt.close()

    
    def checkPoint(self, block_vec, agentPos, agentRot):
        yAxisRot = agentRot[0]
        xAxisRot = agentRot[1]
        
        # Translate block vec to original coordinates
        # unrotate about y axis
        new_block_vec = self.rotateY(block_vec, math.radians(yAxisRot))
        
        # unrotate about x axis
        new_block_vec = self.rotateX(new_block_vec, math.radians(xAxisRot))
        
        # untranslate x, y, z
        new_block_vec = self.translate(new_block_vec, (-agentPos[0], -agentPos[1], -agentPos[2]))
        #print ("Block vec", new_block_vec)

        # check if block is in xz FOV
        # check if block is in yz FOV
        if (self.isBlockInXZ_FOV(new_block_vec) and self.isBlockInYZ_FOV(new_block_vec)):
            #print ("FOV point: ", new_block_vec[0], new_block_vec[1], new_block_vec[2])  
            return True
            
        return False
        
        
    def rotateX(self, vec, theta):
        mat = np.array([[1, 0, 0], 
                        [0, np.cos(theta), -np.sin(theta)],
                        [0, np.sin(theta), np.cos(theta)]])
        return np.dot(mat, vec)
    
        
    def rotateY(self, vec, theta):
        mat = np.array([[np.cos(theta), 0, np.sin(theta)], 
                        [0, 1, 0],
                        [-np.sign(theta), 0, np.cos(theta)]])
        return np.dot(mat, vec)
    
        
    def rotateZ(self, vec, theta):
        mat = np.array([[np.cos(theta), -np.sin(theta), 0], 
                        [np.sin(theta), np.cos(theta), 0],
                        [0, 0, 1]])
        return np.dot(mat, vec)
    
    
    def translate(self, vec, dvec):
        mat = np.array([[1, 0, 0, dvec[0]],
                        [0, 1, 0, dvec[1]],
                        [0, 0, 1, dvec[2]],
                        [0, 0, 0, 1]])
        vecAnd1 = np.array([vec[0], vec[1], vec[2], 1])
        return np.dot(mat, vecAnd1)[:3]
    
    
    def getEquivAtZero(self, angle):
        return angle % 360 - 180           
    
      
    def isBlockInXZ_FOV(self, blockPos):
        """
        Agent position is assumed to be 0,0,0 looking in -Z direction
        """
        bx, by, bz = blockPos

        opp = bx
        adj = bz
        #if (adj == 0 or opp == 0): return False
        theta = math.atan2(opp, adj)
        degs = math.degrees(theta)
        degs = self.getEquivAtZero(degs)
        #print "XZ: ", (blockPos, degs)
        return math.fabs(degs) <= (FOV_PLAYER / 2.0)

        
    def isBlockInYZ_FOV(self, blockPos):
        """
        Agent position is assumed to be 0,0,0 looking in -Z direction
        """
        bx, by, bz = blockPos
        
        opp = by # minus so that in first quadrant, since looking towards negative z
        adj = bz
        #if (adj == 0 or opp == 0): return False
        theta = math.atan2(opp, adj)
        degs = math.degrees(theta)
        degs = self.getEquivAtZero(degs)
        #print "YZ: ", (blockPos, degs)
        return math.fabs(degs) <= (FOV_PLAYER / 2.0)
        
        
    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
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
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.player.dy = 0
                    break
        return tuple(p)


        




    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """

        if symbol == key.P:
            print "SAVING WORLD!"
            self.model.saveWorld()
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
            pyglet.app.exit()


    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        pass


    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # label
        #self.label.y = height - 10
        
        # reticle
        # if self.reticle:
        #     self.reticle.delete()
        # x, y = self.width / 2, self.height / 2
        # n = 10
        # self.reticle = pyglet.graphics.vertex_list(4,
        #     ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        # )


    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    
    def on_draw(self):
        """ Called by pyglet to draw the canvas."""
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_labels()
        #self.draw_reticle()
        
        
    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.player.get_sight_vector()
        block = self.model.hit_test(self.player.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_labels(self):
        """ Draw the label in the top left of the screen.

        """
        #x, y, z = self.position
        #self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d -- Current spell: %s' % (
        #    pyglet.clock.get_fps(), x, y, z,
        #    len(self.model._shown), len(self.model.world), str(self.current_spell))
        #self.label.text = 'Spell: %s' % (str(self.player.current_spell))
        #self.label.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        



def setup_fog():
    """ Configure the OpenGL fog properties.

    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def opengl_setup():
    """ Basic OpenGL configuration.

    """
    # Set the color of "clear", i.e. the sky, in rgba.
    #glClearColor(0.5, 0.69, 1.0, 1)
    glClearColor(1, 1, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()
    
    # Setup grayscale conversion color component scaling values
    glPixelTransferf(GL_RED_SCALE, 0.299)
    glPixelTransferf(GL_GREEN_SCALE, 0.587)
    glPixelTransferf(GL_BLUE_SCALE, 0.114)

"""

def main():
    window = Window(width=VIEW_WINDOW_SIZE, height=VIEW_WINDOW_SIZE, caption='MindCraft', resizable=True, vsync=False)
    
    #p = Player()
    p = DeepMindPlayer()
    
    window.set_player(p)
    p.setGame(window)
    world_file = "test%d.txt" % random.randrange(10)
    generateGameWorld(world_file)
    window.model.loadMap("maps/%s" % world_file)

    opengl_setup()
    
    #pyglet.app.run()
    return window


def step(window):
    pyglet.clock.tick()
    window.update(100)  # fake ms of time pass
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()
    #time.sleep(2)

    
"""
