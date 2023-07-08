
"""
@author     
@org        MSc '24, Brandenburgische Technische Universität Cottbus-Senftenberg
@date       2023-05-05
"""

"""
Calibration scenario for (game)error related potentials:
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

import random as rdm
from time import time
import math, sys, colorsys, random
import meyendtris
# import numpy as np
from direct.gui.OnscreenImage import OnscreenImage

from meyendtris.framework.basicstimuli import BasicStimuli
from direct.showbase.ShowBase import ShowBase


class Main(BasicStimuli):
    def __init__(self):
        super().__init__()
        self._base = meyendtris.__BASE__
        
        self.trial = 10
        self.duration = 30

        self.textPressSpace = "Press space to continue"     # text to display before beginning
        self.textEndExperiment = "End of experiment \nPress 'escape' to exit"        # text to indicate end of experiment

        self.beepSound = meyendtris.path_join("/media/ding.wav")
        self.beepVolume = 1.0

        self.image = meyendtris.path_join('/media/blank.tga')

        self.framecolour = (0.92, 0.96, 0.11, 0.7)
        self.squarecolour = (0.2, 0.6, 1, 0.7)
    
    def start_calibration(self):
        self.accept("escape", sys.exit)
        # initialising beep audio
        beep = self._base.loader.loadSfx(self.beepSound)
        beep.setVolume(self.beepVolume)
        beep.setLoop(False)

        self.write(text = self.textPressSpace, duration = 'space')

        for trial in range(self.trial): #Begin trial series
            #Progress bar for errors(maxed out at 5 errors)
            Pg_bar_right = (0.1,1.3,-0.8,-0.9)
            Pg_bar_left = (-0.1,-1.3,-0.8,-0.9)
            
            pg_block_right = [0.1,0.1,-0.8,-0.9]
            pg_block_left = [-0.1,-0.1,-0.8,-0.9]
            block_increment = (Pg_bar_right[1] - Pg_bar_right[0])/5

            blocks_rt, blocks_lt = [], []

            self.marker(f"Begin err trial {trial+1}")
            err_left,err_right = 0,0 #error count

            while err_left <5 and err_right <5: #Single trial
                beep.play()
                self.sleep(1)

                target_right = 1 if random.random()>0.5 else 0 #Ranomized target direction
                dir_text = "Right" if target_right else "Left"
                self.write("Move "+dir_text, duration=2)
                # TODO register keypress here
                #Left arrow for left movement and Right arrow for right movement
                self.marker("Arrow Keypress")
                
                #progerss bars
                frame_rt = self.frame(
                    rect=(Pg_bar_right),
                    duration=self.duration + 1,
                    color=self.framecolour,
                    block=False
                )
                frame_lt = self.frame(
                    rect=(Pg_bar_left),
                    duration=self.duration + 1,
                    color=self.framecolour,
                    block=False
                )

                error_movement = 1 if random.random()<=0.4 else 0 #Randomized error probablity

                if target_right:
                    if error_movement: #Target directio right and actual movement left
                        pg_block_right[1]+=block_increment
                        err_right += 1
                        err_bar_rt = self.rectangle(tuple(pg_block_right),
                                    duration=0,
                                    block=True,
                                    color=(0.8,0.92,0.74,0.5),
                                    parent=None,      # the renderer to use for displaying the object
                                    depth=0,)
                        blocks_rt.append(err_bar_rt)
                        arrow = OnscreenImage(image=meyendtris.path_join('/media/arrow_left.png'), scale=(0.3,1,0.3))
                        arrow.setTransparency(1)
                        self.marker("Error movement")
                        self.marker("Error movement right")
                    else:
                        arrow = OnscreenImage(image=meyendtris.path_join('/media/arrow_right.png'), scale=(0.3,1,0.3))
                        self.marker("Non-Error movement")
                        self.marker("Non-Error movement right")
                        arrow.setTransparency(1)
                else:
                    if error_movement: #Target direction left and actual movement right
                        pg_block_left[1]-=block_increment
                        err_left += 1
                        err_bar_lt = self.rectangle(tuple(pg_block_left),
                                    duration=0,
                                    block=True,
                                    color=(0.8,0.92,0.74,0.5),
                                    parent=None,      # the renderer to use for displaying the object
                                    depth=0,)
                        blocks_lt.append(err_bar_lt)
                        arrow = OnscreenImage(image=meyendtris.path_join('/media/arrow_right.png'), scale=(0.3,1,0.3))
                        arrow.setTransparency(1)
                        self.marker("Error movement")
                        self.marker("Error movement left")
                    else:
                        arrow = OnscreenImage(image=meyendtris.path_join('/media/arrow_left.png'), scale=(0.3,1,0.3))
                        arrow.setTransparency(1)
                        self.marker("Non-Error movement")
                        self.marker("Non-Error movement left")

                self.sleep(random.randint(2,3)) #Randomized interval to prevent habituation
                arrow.destroy()

            self.write(f"trial {trial+1} complete. Press space to begin next trail",duration = 'space')
            for block in blocks_rt:
                block.destroy()
            for block in blocks_lt:
                block.destroy()

        self.write(text = self.textEndExperiment, duration = 'space')

    def run(self):
        self.start_calibration()
