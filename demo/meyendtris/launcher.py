'''
The SNAP experiment launcher program. To be run on the subject's PC.

* Installation notes: see INSTALLATION NOTES.TXT

* This program can launch experiment modules that are specified in the modules directory
  (one at a time).

* The module to be launched (and various other options) can be specified at the command line; here is a complete listing of all possible config options and their defaults:
  launcher.py --MODULENAME relaxation.calibration --STUDYPATH studies/Sample1 --AUTOLAUNCH 1 --DEVELOPER 1 --engineconfig defaultsettings.prc --DATARIVER 0 --LABSTREAMING 1 --FULLSCREEN 0 --WINDOWSIZE 800x600 --WINDOWORIGIN 50/50 --NOBORDER 0 --NOMOUSECURSOR 0 --TIMECONSUMPENSATE 1
    
* If in DEVELOPER mode, several key bindings are enabled:
   Esc: exit program
   F1: start module
   F2: cancel module
  
* In addition to modules, there are "study configuration files" (aka study configs),
  which are in in the studies directory. These specify the module to launch in the first line
  and assignments to member variables of the module instance in the remaining lines (all Python syntax allowed).
  
  A config can be specified in the command line just by passing the appropriate .cfg file name, as in the following example.
  In addition, the directory where to look for the .cfg file can be specified as the STUDYPATH.
  launcher.py --module=test1.cfg --STUDYPATH=studies/DAS
  
* The program can be remote-controlled via a simple TCP text-format network protocol (on port 7899) supporting the following messages:
  start                  --> start the current module
  cancel                 --> cancel execution of the current module
  load modulename        --> load the module named modulename
  config configname.cfg  --> load a config named configname.cfg (make sure that the STUDYPATH is set correctly so that it's found)
  setup name=value       --> assign a value to a member variable in the current module instance
                             can also involve multiple assignments separated by semicolons, full Python syntax allowed.
   
* The underlying Panda3d engine can be configured via a custom .prc file (specified as --engineconfig=filename.prc), see
  http://www.panda3d.org/manual/index.php/Configuring_Panda3D
  
* For quick-and-dirty testing you may also override the launch options below under "Default Launcher Configuration", but note that you cannot check these changes back into the main source repository of SNAP.  
    
'''
import sys, os
import warnings
from argparse import ArgumentParser
import threading
import queue
import socketserver
import importlib

from direct.task.Task import Task
from panda3d.core import loadPrcFile, loadPrcFileData

import meyendtris
from meyendtris.framework.eventmarkers.eventmarkers import send_marker, init_markers
import meyendtris.framework.base_classes

import zmq
import logging
from zmq.log.handlers import PUBHandler
from meyendtris.server import Server

SNAP_VERSION = '2.0'
logger = logging.getLogger("meyendtris")
logging.basicConfig(level=logging.DEBUG)

# -----------------------------------------------------------------------------------------
# --- Default Launcher Configuration (selectively overridden by command-line arguments) ---
# -----------------------------------------------------------------------------------------

# This is the module that will be initially loaded if nothing
# else is specified.
# Can also be a .cfg file of a study.
# provide a .py that Main() ex: "concentration.calibration". Assumes to load it from modules/ folder
LOAD_MODULE = "relaxation.calibration"

# If true, the selected module will be launched automatically; otherwise it will
# only be (pre-)loaded; the user needs to press F1 (or issue the "start" command remotely) to start the module 
AUTO_LAUNCH = True

# The directory in which to look for .cfg files, if passed as module or via
# remote control messages.
STUDY_PATH = "meyendtrisdisplaysettings.prc"

# Set this to True or False to override the settings in the engineconfig file (.prc)
FULL_SCREEN = False

# Set this to a resolution like "1024x768" (with quotes) to override the settings in the engineconfig file
WINDOW_SIZE = "1024x768"

# Set this to a pixel offset from left top corner, e.g. "50/50" (with quotes) to override the window location in the engineconfig file
WINDOW_ORIGIN = "50/50"

# Set this to True or False to override the window border setting in the engineconfig file
NO_BORDER = True

# Set this to True or False to override the mouse cursor setting in the engineconfig file
NO_MOUSECURSOR = False

# Enable DataRiver support for marker sending.
DATA_RIVER = False

# Enable lab streaming layer support for marker sending.
LAB_STREAMING = True

# This is the default port on which the launcher listens for remote control 
# commands (e.g. launching an experiment module)
SERVER_PORT = 7897

# Whether the Launcher starts in DEVELOPER mode; if true, modules can be loaded,
# started and cancelled via keyboard shortcuts (not recommended for production 
# experiments)
DEVELOPER_MODE = True

# Whether lost time (e.g., to processing or jitter) is compensated for by making the next sleep() slightly shorter
COMPENSATE_LOST_TIME = True



# -----------------------------------
# --- Main application definition ---
# -----------------------------------

class MainApp:
    """The Main SNAP application.
    Pass either commandline arguments or use the global variables or the init varibles.
    There are 3 ways to control the MainApp.
    """
    def __init__(
            self,
            modulename=LOAD_MODULE,
            studypath=STUDY_PATH,
            fullscreen=FULL_SCREEN,
            windowsize=WINDOW_SIZE,
            windoworigin=WINDOW_ORIGIN,
            noborder=NO_BORDER,
            nomousecursor=NO_MOUSECURSOR,
            datariver=DATA_RIVER,
            labstreaming=LAB_STREAMING,
            serverport=SERVER_PORT,
            developer=DEVELOPER_MODE,
            timecompensate=COMPENSATE_LOST_TIME,
            autolaunch=AUTO_LAUNCH, **kwargs):
        """Needs a modulename to load and execute, pass it in global variable LOAD_MODULE or as cmdline args, --modulename
        """
        # load the parameters from kwargs, if passed any
        self._base = meyendtris.__BASE__
        self._module = kwargs.get("MODULENAME") if kwargs.get("MODULENAME") else modulename
        self._labstreaming = kwargs.get("LABSTREAMING") if kwargs.get("LABSTREAMING") else labstreaming
        self._datariver = kwargs.get("DATARIVER") if kwargs.get("DATARIVER") else datariver
        self._windowsize = kwargs.get("WINDOWSIZE") if kwargs.get("WINDOWSIZE") else windowsize
        self._windoworigin = kwargs.get("WINDOWORIGIN") if kwargs.get("WINDOWORIGIN") else windoworigin
        self._fullscreen = kwargs.get("FULLSCREEN") if kwargs.get("FULLSCREEN") else fullscreen
        self._noborder = kwargs.get("NOBORDER") if kwargs.get("NOBORDER") else noborder
        self._nomousecursor = kwargs.get("NOMOUSECURSOR") if kwargs.get("NOMOUSECURSOR") else nomousecursor
        self._server_port = kwargs.get("SERVERPORT") if kwargs.get("SERVERPORT") else serverport
        self._developer_mode = kwargs.get("DEVELOPER") if kwargs.get("DEVELOPER") else developer
        self._compensate_lost_time = kwargs.get("TIMECONSUMPENSATE") if kwargs.get("TIMECONSUMPENSATE") else timecompensate
        self._studypath =  meyendtris.path_join(f'studies/{kwargs.get("STUDYPATH")}') if kwargs.get("STUDYPATH") else path_join(f"studies/{studypath}") # type: ignore
        self._autolaunch = kwargs.get("AUTOLAUNCH") if kwargs.get("AUTOLAUNCH") else autolaunch

        # whether we are executing the module
        self._executing = False

        # preload some data and init some settings
        self._set_defaults()
        self._load_serverconfig()

        # a message queue filled by the TCP server
        self._remote_commands = queue.Queue()
        # instance of the module's Main class
        # load the initial module or config if desired
        self._instance = self._load_module(self._module)
        # Initial markers to be send
        init_markers(self._labstreaming, False, self._datariver)         
        # send an initial start marker
        send_marker(999)

        # register the main loop
        self._main_task = self._base.taskMgr.add(self._main_loop_tick, "main_loop_tick")
        
        # register global keys if desired
        # if (self._developer_mode == "1") or self._developer_mode:
            # self.accept("escape", exit)
            # self.accept("f1",self._remote_commands.put,['start'])
            # self.accept("f2",self._remote_commands.put,['cancel'])
            # self.accept("f5",self._remote_commands.put,['prune'])
        
                
        # start the module if desired
        if self._autolaunch:
            self.start_module()

        # start the TCP server for remote control
        self._init_server(self._server_port)

    def _load_serverconfig(self):
        if os.path.exists(self._studypath):
            print("Applying the engine configuration file/settings...")
            # load the selected engine configuration (STUDYPATH takes precedence over the SNAP root path)
            loadPrcFile(self._studypath)
        else:
            warnings.warn("Studies .prc file not loaded. Loading defaultsettings.prc ...")
            loadPrcFile(meyendtris.path_join("studies/defaultsettings.prc"))

        # override engine settings according to the command line arguments, if specified
        loadPrcFileData('', f'FULLSCREEN {self._fullscreen}')
        loadPrcFileData('', f"win-size {self._windowsize.replace('x',' ')}") # type: ignore
        loadPrcFileData('', f"win-origin {self._windoworigin.replace('/',' ')}") # type: ignore
        loadPrcFileData('', f'undecorated {self._noborder}')
        loadPrcFileData('', f'NOMOUSECURSOR {self._nomousecursor}')

    def _set_defaults(self):
        """Sets some environment defaults that might be overridden by the modules."""
        font = self._base.loader.loadFont(meyendtris.path_join('media/arial.ttf'), textureMargin=5) # type: ignore
        font.setPixelsPerUnit(128)
        # self._base.win.setClearColorActive(True)
        # self._base.win.setClearColor((0.3, 0.3, 0.3, 1))
        # winprops = WindowProperties() 
        # winprops.setTitle('SNAP') 
        # self._base.win.requestProperties(winprops)
           
    def _load_module(self, runner):
        """Try to load the given module, if any. The module can be in any folder under modules."""
        if len(runner) > 0:
            try:
                module = importlib.import_module(f'meyendtris.modules.{runner}')
                instance = module.Main() # type: ignore
                instance._make_up_for_lost_time = self._compensate_lost_time
                print(f"module {runner} loaded sucessfully.")
                return instance
            except:
                raise ImportError("Model import Error. \nTip! Check your modules variable path")
        print("Modules variable path needed. CAUTION! you are not running any simulation")

    def _load_remoteconfig(self, name):
        """Try to load a study config file (see studies directory)."""
        print('Attempting to load config "'+ name+ '"...')
        warnings.warn("rewrite this")
            
    # start executing the currently loaded module
    def start_module(self):        
        if self._instance is not None:
            self.cancel_module()
            print('Starting module execution...')
            self._instance.start()
            print('done.')
            self._executing = True

    # cancel executing the currently loaded module (may be started again later)
    def cancel_module(self):
        if (self._instance is not None) and self._executing:
            print('Canceling module execution...')
            self._instance.cancel()
            print('done.')
        self._executing = False
           
    # prune a currently loaded module's resources
    def prune_module(self):
        if (self._instance is not None):
            print("Pruning current module's resources...")
            try:
                self._instance.prune()
            except Exception as inst:
                print("Exception during prune:")
                print(inst)
            print('done.')

            
    # --- internal ---
    def _init_server(self,port):
        """Initialize the remote control server."""
        destination = self._remote_commands 
        class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
            def handle(self):
                try:
                    print("Client connection opened.")
                    while True:
                        data = self.rfile.readline().strip()
                        if len(data)==0:
                            break                        
                        destination.put(data)
                except:
                    print("Connection closed by client.")

        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            pass

        print("Bringing up remote-control server on port", port, "...", end=' ')
        try:
            server = ThreadedTCPServer(("", port),ThreadedTCPRequestHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.setDaemon(True)
            server_thread.start()
            print("done.")
        except:
            print("failed; the port is already taken (probably the previous process is still around).")


    # main loop step, ticked every frame
    def _main_loop_tick(self, task):
        #framework.tickmodule.engine_lock.release()
        meyendtris.framework.base_classes.shared_lock.release()

        # process any queued-up remote control messages
        try:
            while True:
                cmd = str(self._remote_commands.get_nowait()).strip()            
                if cmd == "start":
                    self.start_module()
                elif (cmd == "cancel") or (cmd == "stop"):
                    self.cancel_module()
                elif cmd == "prune":
                    self.prune_module()
                elif cmd.startswith("load "):
                    self._load_module(cmd[5:])
                elif cmd.startswith("setup "):
                    try:
                        exec(cmd[6:], self._instance.__dict__)
                    except:
                        pass
                elif cmd.startswith("config "):
                    if not cmd.endswith(".cfg"):
                        self._load_remoteconfig(cmd[7:]+".cfg")
                    else:
                        self._load_remoteconfig(cmd[7:])
        except queue.Empty:
            pass

        # tick the current module
        if (self._instance is not None) and self._executing:
            self._instance.tick()

        meyendtris.framework.base_classes.shared_lock.acquire()
        #framework.tickmodule.engine_lock.acquire()
        return Task.cont


# ------------------------------
# --- Startup Initialization ---
# ------------------------------
if __name__ == "__main__":
    logger.info(f'This is SNAP version {SNAP_VERSION}')

    # --- Parse console arguments ---
    print('Reading command-line options...')
    parser = ArgumentParser()
    parser.add_argument("-n", "--MODULENAME", dest="MODULENAME", default=LOAD_MODULE,
                    help="Experiment module to load upon startup (see modules). Can also be a .cfg file of a study (see studies and --STUDYPATH).")
    parser.add_argument("-s","--STUDYPATH", dest="STUDYPATH", default=STUDY_PATH,
                    help="The directory in which to look for .cfg files, media, .prc files etc. for a particular study.")
    parser.add_argument("-a", "--AUTOLAUNCH", dest="AUTOLAUNCH", default=AUTO_LAUNCH, 
                    help="Whether to automatically launch the selected module.")
    parser.add_argument("-d","--DEVELOPER", dest="DEVELOPER", default=DEVELOPER_MODE,
                    help="Whether to launch in DEVELOPER mode; if true, allows to load,start, and cancel experiment modules via keyboard shortcuts.")
    parser.add_argument("-f","--FULLSCREEN", dest="FULLSCREEN", default=FULL_SCREEN,
                    help="Whether to go FULLSCREEN (default: according to current engine config).")
    parser.add_argument("-w","--WINDOWSIZE", dest="WINDOWSIZE", default=WINDOW_SIZE,
                    help="Window size, formatted as in --WINDOWSIZE 1024x768 to select the main window size in pixels (default: accoding to current engine config).")
    parser.add_argument("-o","--WINDOWORIGIN", dest="WINDOWORIGIN", default=WINDOW_ORIGIN,
                    help="Window origin, formatted as in --WINDOWORIGIN 50/50 to select the main window origin, i.e. left upper corner in pixes (default: accoding to current engine config).")
    parser.add_argument("-b","--NOBORDER", dest="NOBORDER", default=NO_BORDER,
                    help="Disable window borders (default: accoding to current engine config).")
    parser.add_argument("-c","--NOMOUSECURSOR", dest="NOMOUSECURSOR", default=NO_MOUSECURSOR,
                    help="Disable mouse cursor (default: accoding to current engine config).")
    parser.add_argument("-r","--DATARIVER", dest="DATARIVER", default=DATA_RIVER,
                    help="Whether to enable DataRiver support in the launcher.")
    parser.add_argument("-l","--LABSTREAMING", dest="LABSTREAMING", default=LAB_STREAMING,
                    help="Whether to enable lab streaming layer (LSL) support in the launcher.")
    parser.add_argument("-p","--SERVERPORT", dest="SERVERPORT", default=SERVER_PORT,
                    help="The port on which the launcher listens for remote control commands (e.g. loading a module).")
    parser.add_argument("-t","--TIMECONSUMPENSATE", dest="TIMECONSUMPENSATE", default=COMPENSATE_LOST_TIME,
                    help="Compensate time lost to processing or jitter by making the successive sleep() call shorter by a corresponding amount of time (good for real time, can be a hindrance during debugging).")
    args = parser.parse_args()

    # ----------------------
    # --- SNAP Main Loop ---
    # ----------------------
    server = Server(log=True)
    app = MainApp(**vars(args))

    # Needed after the call to MainApp
    while True:
        meyendtris.framework.base_classes.shared_lock.acquire()
        #framework.tickmodule.engine_lock.acquire()
        app._base.taskMgr.step()
        #framework.tickmodule.engine_lock.release()
        meyendtris.framework.base_classes.shared_lock.release()
    # --------------------------------
    # --- Finalization and cleanup ---
    # --------------------------------
    print('Terminating launcher...')