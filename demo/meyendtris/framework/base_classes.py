"""
Base class for all tick()-based modules.
"""
from abc import ABC, abstractmethod
from direct.showbase.DirectObject import DirectObject
import threading

# this lock makes sure that only one chunk of code runs at a time
# (tick, render, event handling or script code)
shared_lock = threading.RLock()

# this lock is currently unused by it intended to lock the Panda3d engine from concurrent access by either
# Tickmodules or other threads (e.g., network handlers).
engine_lock = threading.RLock()

class TickModule(DirectObject, ABC):
    def __init__(self):
        """
        Construct a new module and pre-load any data if necessary.
        
        Derive from this module if you are making a simple game or test with not 
        too much sequential state (such as blocks, trials, pauses, etc). An example
        would be a bouncing or brain-controlled ball.

        Preferably this function should only assign default values and arguments defer any further initialization code
        to the start() function (or run() function if you're using a LatentModule) since the default values may be
        overridden by the experimenter or config files before he/she invokes start().
        """
        super().__init__()

    # ======================
    # === core interface ===
    # ======================

    @abstractmethod
    def start(self):
        """ Start execution of the module, i.e. initialize whatever is necessary. """
        pass
    
    @abstractmethod
    def cancel(self):
        """ Cancel execution of the module. Remove any objects from the screen, audio buffers, event handlers, etc. """
        pass
    
    @abstractmethod
    def tick(self):
        """ Advance the internal state of the module, called once per frame. """
        pass
    
    @abstractmethod
    def prune(self):
        """ Optionally prune large resources (e.g. textures) that may have been loaded during __init__ to make space for the next module. """
        pass

class TimeConsumingModule(DirectObject, ABC):
    def __init__(self):
        """
        Abstract Base Class for the time consuming function that are to be inherited in LatentModule
        """
        super().__init__()
    
    @abstractmethod
    def sleep(self, duration):
        """
        Sleep for a number of seconds;
        """
        pass
    
    @abstractmethod
    def waitfor(self, eventid, duration):            
        """
        Wait until a specified event occurs or a number of seconds has passed;
        """
        pass
    