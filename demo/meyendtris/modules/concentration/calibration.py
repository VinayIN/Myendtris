# -*- coding: utf-8 -*-

"""
@author     Binay Kumar Pradhan, Farahnaz Khorasaninia
@org        MSc '24, Brandenburgische Technische Universität Cottbus-Senftenberg
@date       2023-05-16
"""

"""
Calibration scenario for concentration:
Calibration scenario for Distraction:
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
import meyendtris
import sys
import random
import numpy as np
from meyendtris.framework.basicstimuli import BasicStimuli
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import Point3


class Main(BasicStimuli):
    def __init__(self):
        super().__init__()
        self._base = meyendtris.__BASE__
        
        self.trial = 5
        self.duration = 30

        self.textPressSpace = "Press space to continue"     # text to display before beginning
        self.textEndExperiment = "End of experiment"        # text to indicate end of experiment

        self.beepSound = meyendtris.path_join("/media/ding.wav")
        self.beepVolume = 1.0

        self.image = meyendtris.path_join('/media/blank.tga')

        self.framecolour = (0.92, 0.96, 0.11, 0.7)
        self.squarecolour = (0.2, 0.6, 1, 0.7)

    def run(self):
        # initialising beep audio
        beep = self._base.loader.loadSfx(self.beepSound)
        beep.setVolume(self.beepVolume)
        beep.setLoop(False)

        self.write(text = self.textPressSpace, duration = 'space')
        random_question = [
            "How much liters of water did you drink today?",
            "How many birds did you see today? Do you remember the color of the bird?",
            "When did you wake up today?",
            "Did you met any of your friends today? What is his/her last name?",
            "What color shoes are you wearing?"
        ]
        block_moving_count = int(np.ceil(self.duration * 0.4))
        for trial in range(self.trial):
            self.marker(f"Distraction trial {trial+1}")
            self.write(text=f"Trial {trial} \n\n {random.choice(random_question)}", duration=5)
            beep.play()
            self.sleep(1)
            self.frame(
                rect=(-0.5,0.5,0.5,-0.5),
                duration=self.duration + 1,
                color=self.framecolour,
                block=False
            )

            duration_array = np.concatenate(
                (
                np.ones(block_moving_count),
                np.array([self.duration-(block_moving_count)]),
                np.ones(1)),
                axis=None)
            for idx, duration in enumerate(duration_array):
                self.marker("Distraction square")
                l = 2*random.random() - 1
                r = 2*random.random() - 1
                t = 2*random.random() - 1
                b = 2*random.random() - 1
                self.rectangle(
                    rect=(l,r,t,b),
                    duration=duration,
                    color=self.squarecolour)
            
            self.marker("Final Response")
            self.rectangle(
                    rect=(-0.25, 0, 0.25, 0.25),
                    duration=1,
                    color=self.squarecolour)
        self.write(text = self.textEndExperiment, duration = 'space')
        sys.exit()