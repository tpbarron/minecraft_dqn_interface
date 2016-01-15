from game import *
from game_config import *
from game_globals import *
import time

window = None
itrCount = 0

def init():
    """ 
    Initialize the game state
    """
    global window
    window = Window(width=VIEW_WINDOW_SIZE, height=VIEW_WINDOW_SIZE, caption='Minecraft', resizable=False, vsync=False)
    p = DeepMindPlayer()
    window.set_player(p)
    p.setGame(window)
    world_file = "/test%d.txt" % random.randrange(10)
    generateGameWorld(world_file)
    window.model.loadMap(world_file)
    opengl_setup()
    return "Successfully initialized"



def step():
    global window
    dt = pyglet.clock.tick()
    screen = window.update(dt * 1000)
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()
    return screen
    
    
def get_action_set():
    """
    Get a list of all the legal actions
    """
    return LEGAL_ACTIONS

    
def get_screen():
    """
    Do one step of the game state and get the current screen
    """
    # do one step 
    global itrCount 
    itrCount += 1
    screen = step()
    #print ("py screen")
    #print screen
    #print len(list(screen))
    #print list(screen)
    return list(screen)


def act(action):
    """
    Perform the desired action
    """
    global window
    #print "Performing action ", action
    return window.player.doAction(action) 
    

def is_game_over():
    """
    Determine if the game is over
    """
    global itrCount
    return itrCount >= MAXIMUM_GAME_FRAMES or window.player.endGameEarly()


def reset():
    """
    Reset the game state
    """
    global itrCount
    global window
    itrCount = 0
    window.reset()
    
    
if __name__ == "__main__":
    init()
    i = 0
    while i < 1000:
        img = get_screen()
        #cv2.imwrite("image.png", img)
        over = is_game_over()
        if (over):
            reset()
        else:
            pass
            #act(3)
        i += 1
        #time.sleep(2)
              

