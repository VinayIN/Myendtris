# -*- coding: utf-8 -*-

"""
@author     Laurens R Krol
@org        Team PhyPA, Technische Universitaet Berlin
@date       2014-10-10
"""

"""
Simple vertical bar that changes its height depending on the value of self.bci.
This value must be set externally, which SNAP allows to be done through TCP, by
sending the string 'setup self.bci=1.5' (or any other number) to port 7897 of 
the computer on which SNAP is running (unless another port has been set).
BCILAB has a built-in function to communicate with SNAP.
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
import sys
import meyendtris
from meyendtris.framework.basicstimuli import BasicStimuli
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import PerlinNoise2


class Main(BasicStimuli):
    def __init__(self):
        super().__init__()
        self._base = meyendtris.__BASE__ 
        self.fps = 60                               # update frequency, in Hz
        self.simulateData = False                   # whether or not to simulate data. if not, self.bci must be set externally.
        self.perlinStepSize = .005                  # step size for perlin noise in case of simulated data   
        self.inputRange = [1, 2]                    # range of the incoming signal (self.bci)    
        self.useThresholds = False                  # whether or not to only accept input values below/above certain thresholds
        self.bciThresholds = [1.2, 1.8]             # thresholds
        self.barColour = (0.20, 0.00, 0.60, 1.00)   # colour of the bar
        self.frameHeight = 0.75                     # Height of the frame
        self.frameWidth = 0.01                      # width of the frame     
        self.bci = 1.5                              # input value placeholder
        self.mental_states = ["relaxation", "concentration", "error"]
        

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
        
    def simulate_bar(self, mental_state):
        bar_width = self.frameWidth * 20
        # drawing frame
        frameBorder = OnscreenImage(
            image=meyendtris.path_join('media/blank.tga'),
            pos = (0, 0, 0),
            color = (1, 1, 1, 0.5),
            scale = (bar_width, 0, self.frameHeight))
        frameBorder.setTransparency(1)

        framecenter = OnscreenImage(
            image=meyendtris.path_join('media/blank.tga'),
            pos = (0, 0, 0),
            color = (1, 1, 1, 1),
            scale = (0.2, 0, self.frameWidth))
        framecenter.setTransparency(1)
        
        frameInner = OnscreenImage(
            image=meyendtris.path_join('media/blank.tga'),
            pos = (0, 0, 0),
            color = (0, 0, 0, 1),
            scale = (bar_width - 2 * self.frameWidth, 0, self.frameHeight - 2 * self.frameWidth))
        frameInner.setTransparency(1)
        
        # drawing bar
        bar = OnscreenImage(
            image=meyendtris.path_join('media/blank.tga'),
            color = self.barColour)
        bar.setTransparency(1)
        

        perlin = PerlinNoise2(1, 1)
        perlinCount = 0
        bufferLength = int(self.fps * 2) 
        bufferList = [(self.inputRange[1] - self.inputRange[0]) / 2] * bufferLength
    
        self.loop = True
        def loop_false(): self.loop=False
        while self.loop:
            self.accept("n", loop_false)
            if self.simulateData:
                # simulating input
                self.bci = perlin.noise(perlinCount)
                self.bci = self.map(self.bci, [-1, 1], self.inputRange)
                perlinCount += self.perlinStepSize
                
            if self.useThresholds:
                if self.bci < self.bciThresholds[0] or self.bci > self.bciThresholds[1]:
                    # appending input only if it is beyond the thresholds
                    bufferList.append(self.bci)
                    bufferList = bufferList[1:]
            else:
                # always appending input
                bufferList.append(self.bci)
                bufferList = bufferList[1:]
            
            # taking bufferList mean as current value
            currentValue = sum(bufferList) / len(bufferList)
                
            # redrawing bar
            maxHeight = self.frameHeight - 4 * self.frameWidth
            currentBarHeight = self.map(currentValue, self.inputRange, [0, maxHeight])                
            bar.setScale(bar_width - 4 * self.frameWidth, 0, currentBarHeight)
            bar.setPos((0, 0, -self.frameHeight + 4 * self.frameWidth + currentBarHeight))
            self.sleep(1.0 / self.fps)

    def run(self):
        # accepting keyboard input
        self.accept("escape", sys.exit)
        for mental_state in self.mental_states:
            caption = self.write(
                text=f"{mental_state}: Classifier\n(Press 'n' for next mental state)",
                pos=(0, -0.8),
                duration=0)
            self.simulate_bar(mental_state)
            caption.destroy()
        self.write(
            text="End of experiment. \nPress 'escape' to exit",
            pos=(0, -0.8),
            duration=0)
        
        
        
        