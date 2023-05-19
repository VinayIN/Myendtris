# -*- coding: utf-8 -*-

"""
@author     Laurens R Krol
@org        Team PhyPA, Technische Universitaet Berlin
@date       2014-10-10
"""

"""
Simple alpha calibration module. Presents either a simple crosshair,
or flickering coloured rectangles. Writes a marker every second
indicating the condition: "relax" for the crosshair, "chaos" for the
rectangles. Writes additional markers indicating the position within
each trial (e.g. "relax0", "relax1" etc.).

During chaos, the participant's task is, for example, to "count all
the pink rectangles". This is not supposed to be accurately possible,
but designed to keep them engaged. When the crosshair is visible,
participants are instructed to relax. Specifically, this can be done
by calling to mind very specific details of one and the same memory.
"""

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from framework.latentmodule import LatentModule
from panda3d.core import PerlinNoise2, TextProperties, TextPropertiesManager, TextNode
from random import random
from time import time


class Main(LatentModule):
    def __init__(self):
        LatentModule.__init__(self, make_up_for_lost_time = False)

        self.backgroundColour = (0, 0, 0, 1)        # background colour    
        
        self.fps = 60                               # update frequency, in Hz

        self.trials = 20                            # total number of trials (e.g. 2 = one of each)
        self.trialLength = 10                       # length per trial in seconds (only integers)
        
        self.beepSound = "ding.wav"                 # audio file for beep
        self.beepVolume = 1.0                       # beep volume, 0-1
        
        self.crossColour = (0.2, 0.2, 0.2, 1)       # crosshair colour
        
        self.maxSquares = 10                        # maximum number of squares on the screen

        self.textPressSpace = "Press space to continue"     # text to display before beginning
        self.textEndExperiment = "End of experiment"        # text to indicate end of experiment
        self.textColour = (0.5, 0.5, 0.5, 1)                # text colour (r, g, b, a)
        

    def waitForUser(self):
        # waiting for user to be ready
        self.write(
                text = "\1text\1" + self.textPressSpace,
                duration = 'space')
        

    def map(self, sourcevalue, sourcerange, targetrange):
        # mapping a value from one range onto another
        
        # converting source range into a 0-1 range
        sourceSpan = sourcerange[1] - sourcerange[0]
        if sourceSpan == 0 or sourcevalue == float("-inf"):
            return targetrange[0]
        elif sourcevalue == float("inf"):
            return targetrange[1]
        valueScaled = float(sourcevalue - sourcerange[0]) / sourceSpan

        # converting the 0-1 range into a value in the right range
        targetSpan = targetrange[1] - targetrange[0]
        targetValue = targetrange[0] + (valueScaled * targetSpan)

        # fixing it within the target range
        if targetValue < min(targetrange):
            targetValue = min(targetrange)
        elif targetValue > max(targetrange):
            targetValue = max(targetrange)

        return targetValue
        

    def run(self):
        # accepting keyboard input
        self.accept("escape", self.exit)
    
        # setting black background colour
        base.win.setClearColor(self.backgroundColour)
        
        # setting text colour
        tp = TextProperties()
        tp.setTextColor(self.textColour)
        tpMgr = TextPropertiesManager.getGlobalPtr()
        tpMgr.setProperties("text", tp)
                
        # initialising beep audio
        beep = base.loader.loadSfx(self.beepSound)
        beep.setVolume(self.beepVolume)
        beep.setLoop(False)
        
        self.waitForUser()

        noise = []
        for trial in range(self.trials):
            # starting of trial: sounding bell, waiting
            beep.play()            
            self.sleep(2)
            
            if trial % 2 == 0:
                """ Condition: Relax """
                
                for second in range(self.trialLength):
                    self.marker("relax")
                    self.marker("relax" + str(second))
                    
                    # showing crosshair
                    self.crosshair(
                            duration = 1,
                            color = self.crossColour)
            else:
                """ Condition: Chaos """
                
                for second in range(self.trialLength):
                    self.marker("chaos")
                    self.marker("chaos" + str(second))
                    
                    # showing visual noise
                    startTime = time()
                    while time() < startTime + 1:
                    
                        red, green, blue, alpha, height = random(), random(), random(), random(), random()
                        width = self.map(random(), [0, 1], [-base.getAspectRatio(), base.getAspectRatio()])
                        x     = self.map(random(), [0, 1], [-base.getAspectRatio(), base.getAspectRatio()])
                        y     = self.map(random(), [0, 1], [-1, 1])
                        
                        square = self._engine.direct.gui.OnscreenImage.OnscreenImage(image='blank.tga',
                                color = (red, green, blue, alpha),
                                pos = (x, 0, y),
                                scale = (width, 0, height))
                        square.setTransparency(1)
                        noise.append(square)
                        
                        if len(noise) > self.maxSquares:
                            noise[0].destroy()
                            noise = noise[1:]
                
                        self.sleep(1 / self.fps)
                
                for square in noise:
                    square.destroy()
                    
        self.write(
                text = "\1text\1" + self.textEndExperiment,
                duration = 'space')
        self.exit()
        
        
    def exit(self):
        print("Exiting...")
        exit()
        