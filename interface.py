from game import *
from game_config import *
from game_globals import *

window = None
itrCount = 0

def init():
    """ 
    Initialize the game state
    """
    global window
    window = Window(width=VIEW_WINDOW_SIZE, height=VIEW_WINDOW_SIZE, caption='Minecraft', resizable=True, vsync=False)
    p = DeepMindPlayer()
    window.set_player(p)
    p.setGame(window)
    world_file = "/test%d.txt" % random.randrange(10)
    generateGameWorld(world_file)
    window.model.loadMap(world_file)
    setup()
    return "Successfully initialized"


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
    pyglet.clock.tick()
    #TODO: keep track of actual time
    screen = window.update(10)  # fake ms of time pass
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()
    #print len(list(screen))
    #print list(screen)
    return list(screen)


def act(action):
    """
    Perform the desired action
    """
    print "Performing action ", action
    return window.player.doAction(action)


def is_game_over():
    """
    Determine if the game is over
    """
    global itrCount
    return itrCount >= MAXIMUM_GAME_FRAMES


def reset():
    """
    Reset the game state
    """
    global itrCount
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
        i += 1
              

