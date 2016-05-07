from game import *


#from game_config import *
#from game_globals import *
import time

window = None
itrCount = 0

def init(evaluate):
    """
    Initialize the game state
    """
    global window
    print ("Initialing in evaluate mode: ", evaluate)

    if (evaluate):
        window = Window(width=game_config.TEST_WINDOW_SIZE, height=game_config.TEST_WINDOW_SIZE, caption='Minecraft', resizable=False, vsync=False)
    else:
        window = Window(width=game_config.TRAIN_WINDOW_SIZE, height=game_config.TRAIN_WINDOW_SIZE, caption='Minecraft', resizable=False, vsync=False)

    window.set_phase(evaluate)

    p = Player()
    window.set_player(p)
    p.setGame(window)
    world_file = "/test%d.txt" % random.randrange(10)
    p.task.generateGameWorld(world_file)
    window.model.loadMap(world_file)
    opengl_setup()
    return "Successfully initialized"


def get_action_set():
    """
    Get a list of all the legal actions
    """
    #return LEGAL_ACTIONS
    return window.player.task.actions


def get_screen():
    """
    Do one step of the game state and get the current screen
    """
    screen = window.get_screen()
    #print ("py screen")
    #print screen
    #print len(list(screen))
    #print list(screen)
    return list(screen)


def act(action):
    """
    Perform the desired action
    """
    #print ("python act 1")
    global window
    # first apply the action
    window.player.performAction(action)
    #print ("python act 2")
    update()
    #print ("python act 3")
    # now determine the reward from it
    return float(window.player.getReward(action))


def update():
    """
    Updates the game given the currently set params
    Called from act.
    """
    global window
    dt = pyglet.clock.tick()
    window.update(dt * 1000)
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()


def is_game_over():
    """
    Determine if the game is over
    """
    return window.game_over or window.player.endGameEarly()


def reset():
    """
    Reset the game state
    """
    #global itrCount
    global window
    #itrCount = 0
    window.reset()


if __name__ == "__main__":
    init(False)
    i = 0
    total_reward = 0
    while i < 1000:
        img = get_screen()
        #cv2.imwrite("image.png", img)
        over = is_game_over()
        if (over):
            print ("Total reward: ", total_reward)
            total_reward = 0
            print ("Resetting game")
            reset()
        else:
            #pass
            r = act(2)
            total_reward += r
            print ("reward = ", r)
        i += 1
        time.sleep(.05)
