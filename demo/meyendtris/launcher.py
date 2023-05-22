'''
The SNAP experiment launcher program. To be run on the subject's PC.

* Installation notes: see INSTALLATION NOTES.TXT

* This program can launch experiment modules that are specified in the modules directory
  (one at a time).

* The module to be launched (and various other options) can be specified at the command line; here is a complete listing of all possible config options and their defaults:
  launcher.py --module Sample1 --studypath studies/Sample1 --autolaunch 1 --developer 1 --engineconfig defaultsettings.prc --datariver 0 --labstreaming 1 --fullscreen 0 --windowsize 800x600 --windoworigin 50/50 --noborder 0 --nomousecursor 0 --timecompensation 1
    
* If in developer mode, several key bindings are enabled:
   Esc: exit program
   F1: start module
   F2: cancel module
  
* In addition to modules, there are "study configuration files" (aka study configs),
  which are in in the studies directory. These specify the module to launch in the first line
  and assignments to member variables of the module instance in the remaining lines (all Python syntax allowed).
  
  A config can be specified in the command line just by passing the appropriate .cfg file name, as in the following example.
  In addition, the directory where to look for the .cfg file can be specified as the studypath.
  launcher.py --module=test1.cfg --studypath=studies/DAS
  
* The program can be remote-controlled via a simple TCP text-format network protocol (on port 7899) supporting the following messages:
  start                  --> start the current module
  cancel                 --> cancel execution of the current module
  load modulename        --> load the module named modulename
  config configname.cfg  --> load a config named configname.cfg (make sure that the studypath is set correctly so that it's found)
  setup name=value       --> assign a value to a member variable in the current module instance
                             can also involve multiple assignments separated by semicolons, full Python syntax allowed.
   
* The underlying Panda3d engine can be configured via a custom .prc file (specified as --engineconfig=filename.prc), see
  http://www.panda3d.org/manual/index.php/Configuring_Panda3D
  
* For quick-and-dirty testing you may also override the launch options below under "Default Launcher Configuration", but note that you cannot check these changes back into the main source repository of SNAP.  
    
'''
import sys, os
import fnmatch, traceback, warnings
from argparse import ArgumentParser
import threading
import queue
import socketserver


from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import loadPrcFile, loadPrcFileData, Filename, DSearchPath, VBase4

from meyendtris import path_join
from meyendtris.framework.eventmarkers.eventmarkers import send_marker, init_markers
import meyendtris.framework.base_classes


SNAP_VERSION = '2.0'
# -----------------------------------------------------------------------------------------
# --- Default Launcher Configuration (selectively overridden by command-line arguments) ---
# -----------------------------------------------------------------------------------------


# If non-empty, this is the module that will be initially loaded if nothing
# else is specified. Can also be a .cfg file of a study.
LOAD_MODULE = "concentration.calibration"

# If true, the selected module will be launched automatically; otherwise it will
# only be (pre-)loaded; the user needs to press F1 (or issue the "start" command remotely) to start the module 
AUTO_LAUNCH = True

# The directory in which to look for .cfg files, if passed as module or via
# remote control messages.
STUDYPATH = path_join("studies/")

# The default engine configuration.
ENGINE_CONFIG = "defaultsettings.prc"

# Set this to True or False to override the settings in the engineconfig file (.prc)
FULLSCREEN = None

# Set this to a resolution like "1024x768" (with quotes) to override the settings in the engineconfig file
WINDOWSIZE = None

# Set this to a pixel offset from left top corner, e.g. "50/50" (with quotes) to override the window location in the engineconfig file
WINDOWORIGIN = None

# Set this to True or False to override the window border setting in the engineconfig file
NOBORDER = None

# Set this to True or False to override the mouse cursor setting in the engineconfig file
NOMOUSECURSOR = None

# Enable DataRiver support for marker sending.
DATA_RIVER = False

# Enable lab streaming layer support for marker sending.
LAB_STREAMING = True

# This is the default port on which the launcher listens for remote control 
# commands (e.g. launching an experiment module)
SERVER_PORT = 7897

# Whether the Launcher starts in developer mode; if true, modules can be loaded,
# started and cancelled via keyboard shortcuts (not recommended for production 
# experiments)
DEVELOPER_MODE = True

# Whether lost time (e.g., to processing or jitter) is compensated for by making the next sleep() slightly shorter
COMPENSATE_LOST_TIME = True



# -----------------------------------
# --- Main application definition ---
# -----------------------------------

class MainApp(ShowBase):    
    """The Main SNAP application."""
    
    def __init__(self, args):
        super().__init__()

        self._instance = None            # instance of the module's Main class
        self._executing = False          # whether we are executing the module
        self._remote_commands = queue.Queue() # a message queue filled by the TCP server
        self._args = args                # the configuration options

        init_markers(args.labstreaming,False,args.datariver)


        print("Applying the engine configuration file/settings...")
        # load the selected engine configuration (studypath takes precedence over the SNAP root path)
        config_searchpath = DSearchPath()
        config_searchpath.appendDirectory(Filename.fromOsSpecific(args.studypath))
        config_searchpath.appendDirectory(Filename.fromOsSpecific('.'))
        loadPrcFile(config_searchpath.findFile(Filename.fromOsSpecific(args.engineconfig)))

        # add a few more media search paths (in particular, media can be in the media directory, or in the studypath)
        loadPrcFileData('', 'model-path ' + args.studypath + '/media')
        loadPrcFileData('', 'model-path ' + args.studypath)
        loadPrcFileData('', 'model-path media')

        # override engine settings according to the command line arguments, if specified
        if args.fullscreen is not None:
            loadPrcFileData('', 'fullscreen ' + args.fullscreen)
        if args.windowsize is not None:
            loadPrcFileData('', 'win-size ' + args.windowsize.replace('x',' '))
        if args.windoworigin is not None:
            loadPrcFileData('', 'win-origin ' + args.windoworigin.replace('/',' '))
        if args.noborder is not None:
            loadPrcFileData('', 'undecorated ' + args.noborder)
        if args.nomousecursor is not None:
            loadPrcFileData('', 'nomousecursor ' + args.nomousecursor)
            
        # send an initial start marker
        send_marker(999)

        # preload some data and init some settings
        self.set_defaults()

        # register the main loop
        self._main_task = self.taskMgr.add(self._main_loop_tick,"main_loop_tick")
        
        # register global keys if desired
        if args.developer:
            self.accept("escape", exit)
            self.accept("f1",self._remote_commands.put,['start'])
            self.accept("f2",self._remote_commands.put,['cancel'])
            self.accept("f5",self._remote_commands.put,['prune'])
                
        # load the initial module or config if desired
        if args.runner is not None:
            import importlib
            try:
                self.load_module(args.runner)
            except Exception as err:
                print(f"The experiment module '{args.runner}' could not be imported correctly.")
                warnings.warn("module instantiation error")
                traceback.print_exc()
                
        # start the module if desired
        if (args.autolaunch == True) or (args.autolaunch=='1'):
            self.start_module()

        # start the TCP server for remote control
        self._init_server(args.serverport)

        
    def set_defaults(self):
        """Sets some environment defaults that might be overridden by the modules."""
        font = self.loader.loadFont(path_join('media/arial.ttf'), textureMargin=5)
        font.setPixelsPerUnit(128)
        # self.win.setClearColorActive(True)
        # base.win.setClearColor((0.3, 0.3, 0.3, 1))
        # winprops = WindowProperties() 
        # winprops.setTitle('SNAP') 
        # base.win.requestProperties(winprops) 
        
        
    def load_module(self, runner):
        """Try to load the given module, if any. The module can be in any folder under modules."""
        module = ""
        self._instance = module.Main()
        self._instance._make_up_for_lost_time = self._args.timecompensation
        print(f"module {runner} loaded sucessfully.")

    def load_config(self,name):
        """Try to load a study config file (see studies directory)."""
        print('Attempting to load config "'+ name+ '"...')
        warnings.warn("rewrite this")
            
    # start executing the currently loaded module
    def start_module(self):        
        if self._instance is not None:
            self.cancel_module()
            print('Starting module execution...', end=' ')
            self._instance.start()
            print('done.')
            self._executing = True


    # cancel executing the currently loaded module (may be started again later)
    def cancel_module(self):
        if (self._instance is not None) and self._executing:
            print('Canceling module execution...', end=' ')
            self._instance.cancel()
            print('done.')
        self._executing = False

             
    # prune a currently loaded module's resources
    def prune_module(self):
        if (self._instance is not None):
            print("Pruning current module's resources...", end=' ')
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
    def _main_loop_tick(self,task):
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
                    self.load_module(cmd[5:])
                elif cmd.startswith("setup "):
                    try:
                        exec(cmd[6:], self._instance.__dict__)
                    except:
                        pass
                elif cmd.startswith("config "):
                    if not cmd.endswith(".cfg"):
                        self.load_config(cmd[7:]+".cfg")
                    else:
                        self.load_config(cmd[7:])
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
    print('This is SNAP version ' + SNAP_VERSION + "\n\n")

    # --- Parse console arguments ---

    print('Reading command-line options...')
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="runner", default=LOAD_MODULE,
                    help="Experiment module to load upon startup (see modules). Can also be a .cfg file of a study (see studies and --studypath).")
    parser.add_argument("-s","--studypath", dest="studypath", default=STUDYPATH,
                    help="The directory in which to look for .cfg files, media, .prc files etc. for a particular study.")
    parser.add_argument("-a", "--autolaunch", dest="autolaunch", default=AUTO_LAUNCH, 
                    help="Whether to automatically launch the selected module.")
    parser.add_argument("-d","--developer", dest="developer", default=DEVELOPER_MODE,
                    help="Whether to launch in developer mode; if true, allows to load,start, and cancel experiment modules via keyboard shortcuts.")
    parser.add_argument("-e","--engineconfig", dest="engineconfig", default=ENGINE_CONFIG,
                    help="A configuration file for the Panda3d engine (allows to change many engine-level settings, such as the renderer; note that the format is dictated by Panda3d).")
    parser.add_argument("-f","--fullscreen", dest="fullscreen", default=FULLSCREEN,
                    help="Whether to go fullscreen (default: according to current engine config).")
    parser.add_argument("-w","--windowsize", dest="windowsize", default=WINDOWSIZE,
                    help="Window size, formatted as in --windowsize 1024x768 to select the main window size in pixels (default: accoding to current engine config).")
    parser.add_argument("-o","--windoworigin", dest="windoworigin", default=WINDOWORIGIN,
                    help="Window origin, formatted as in --windoworigin 50/50 to select the main window origin, i.e. left upper corner in pixes (default: accoding to current engine config).")
    parser.add_argument("-b","--noborder", dest="noborder", default=NOBORDER,
                    help="Disable window borders (default: accoding to current engine config).")
    parser.add_argument("-c","--nomousecursor", dest="nomousecursor", default=NOMOUSECURSOR,
                    help="Disable mouse cursor (default: accoding to current engine config).")
    parser.add_argument("-r","--datariver", dest="datariver", default=DATA_RIVER,
                    help="Whether to enable DataRiver support in the launcher.")
    parser.add_argument("-l","--labstreaming", dest="labstreaming", default=LAB_STREAMING,
                    help="Whether to enable lab streaming layer (LSL) support in the launcher.")
    parser.add_argument("-p","--serverport", dest="serverport", default=SERVER_PORT,
                    help="The port on which the launcher listens for remote control commands (e.g. loading a module).")
    parser.add_argument("-t","--timecompensation", dest="timecompensation", default=COMPENSATE_LOST_TIME,
                    help="Compensate time lost to processing or jitter by making the successive sleep() call shorter by a corresponding amount of time (good for real time, can be a hindrance during debugging).")
    args = parser.parse_args()

    # ----------------------
    # --- SNAP Main Loop ---
    # ----------------------

    app = MainApp(args)

    # Needed after the call to MainApp
    while True:
        meyendtris.framework.base_classes.shared_lock.acquire()
        #framework.tickmodule.engine_lock.acquire()
        app.taskMgr.step()
        #framework.tickmodule.engine_lock.release()
        meyendtris.framework.base_classes.shared_lock.release()
    # --------------------------------
    # --- Finalization and cleanup ---
    # --------------------------------
    print('Terminating launcher...')