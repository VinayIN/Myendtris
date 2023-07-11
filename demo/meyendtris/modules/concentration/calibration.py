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
        
        self.trial = 20
        self.duration = 30
        self.last_response = 2.5

        self.textPressSpace = "Press space to continue"     # text to display before beginning
        self.textEndExperiment = "End of experiment \nPress 'escape' to exit"        # text to indicate end of experiment

        self.beepSound = meyendtris.path_join("/media/ding.wav")
        self.beepVolume = 1.0

        self.image = meyendtris.path_join('/media/blank.tga')

        self.framecolour = (0.92, 0.96, 0.11, 0.7)
        self.squarecolour = (0.2, 0.6, 1, 0.7)

    def run(self):
        self.accept("escape", sys.exit)
        # initialising beep audio
        beep = self._base.loader.loadSfx(self.beepSound)
        beep.setVolume(self.beepVolume)
        beep.setLoop(False)

        self.write(text = self.textPressSpace, duration = 'space')
        random_question = [
            "How much liters of water did you drink today, to two decimal points?",
            "How many birds did you see today? Do you remember the color of each bird?",
            "When did you wake up today?",
            "Did you met any of your friends today? What is his/her last name?",
            "What color shoes are you wearing? Do you prefer sunglasses or Hat?",
            "Starting today, How many days are left till weekend?",
            "What languages do you speak?",
            "Do you like watching movie or reading book? (Name a title)",
            "How many popes there has been since there the existence of Christianity?",
            "How many EU countries are there to the east of Germany?",
            "How many left turns did you take while arriving to this lab?",
            "How many car brands can you name?",
            "How many letters are there in the alphabet if you remove half of all consonants?",
            "Name the last three professors you saw from your course",
            "Who was the fourth president of your own country?",
            "How much did you spend last month on groceries?",
            "How many courses do you still need to take to graduate?",
            "How many glasses of water do you drink on average?",
            "How many minutes per day do you spend on social media?",
            "Name five animals starting with the letter S."
        ]
        random.shuffle(random_question)
        block_moving_count = int(np.ceil(self.duration * 0.5))
        for idx, trial in enumerate(range(self.trial)):
            if len(random_question) < self.trial:
                raise ValueError("Questions are less, Add some more to the list.")
            self.marker(f"trial {trial+1}/{self.trial}")
            self.write(text=f"Trial {trial+1}/{self.trial}", duration=5)
            self.marker("question key press")
            self.write(text = f"{random_question[idx]} \n\n(Press space when you have read the question)", duration = "space")
            beep.play()
            self.sleep(1)
            self.frame(
                rect=(-0.5,0.5,0.5,-0.5),
                duration=self.duration + self.last_response,
                color=self.framecolour,
                block=False
            )

            duration_array = np.concatenate(
                (
                np.ones(block_moving_count),
                np.array([self.duration-(block_moving_count)]),
                np.array(self.last_response)),
                axis=None)
            for idx, duration in enumerate(duration_array):
                l = 2*random.random() - 1
                r = 2*random.random() - 1
                t = 2*random.random() - 1
                b = 2*random.random() - 1
                if (duration != 1 and duration != self.last_response):
                    self.marker("distraction phase")
                    self.write(text = "Answer the question", duration = 0.5, block=False)
                else: self.marker("concentration phase")
                self.rectangle(
                    rect=(l,r,t,b),
                    duration=duration,
                    block = False if duration == self.last_response else True,
                    color=self.squarecolour)
            self.marker("Final Response")
            response = self.waitfor("enter")
            self.marker(f"response time {response}")
            self.write(text = "How many blocks were inside the frame in this trial? \n\n(Say it loud and press enter)", duration = 'enter')
        self.write(text = self.textEndExperiment, duration = 'space')