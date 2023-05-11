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

from framework.latentmodule import LatentModule
from panda3d.core import PerlinNoise2


class Main(LatentModule):
    def __init__(self):
        LatentModule.__init__(self, make_up_for_lost_time = False)

        self.backgroundColour = (0, 0, 0, 1)        # background colour    
        
        self.fps = 60                               # update frequency, in Hz

        self.simulateData = False                   # whether or not to simulate data. if not, self.bci must be set externally.
        self.perlinStepSize = .005                  # step size for perlin noise in case of simulated data
        
        self.inputRange = [1, 2]                    # range of the incoming signal (self.bci)
        
        self.bufferLength = int(self.fps * 2)       # length of input buffer (buffer mean is displayed as value)
        self.useThresholds = False                  # whether or not to only accept input values below/above certain thresholds
        self.bciThresholds = [1.2, 1.8]             # thresholds
        
        self.barWidth = .15                         # width of the bar
        self.barHeight = .75                        # height of the bar
        self.barColour = (0.20, 0.00, 0.60, 1.00)   # colour of the bar
        
        self.frameWidth = .01                       # width of the frame around the bar
        self.frameColour = (1.00, 1.00, 1.00, 0.50) # colour of the frame around the bar
        
        self.centreVertical = False                 # whether or not the bar's zero-point should be in the centre rather than at the bottom
        
        self.bci = 1.5                             # input value placeholder
        

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

        # drawing frame
        frameBorder = self._engine.direct.gui.OnscreenImage.OnscreenImage(image='blank.tga',
                pos = (0, 0, 0),
                color = self.frameColour,
                scale = (self.barWidth, 0, self.barHeight))
        frameBorder.setTransparency(1)
        
        frameInner = self._engine.direct.gui.OnscreenImage.OnscreenImage(image='blank.tga',
                pos = (0, 0, 0),
                color = self.backgroundColour,
                scale = (self.barWidth - 2 * self.frameWidth, 0, self.barHeight - 2 * self.frameWidth))
        frameInner.setTransparency(1)
        
        # drawing bar
        bar = self._engine.direct.gui.OnscreenImage.OnscreenImage(image='blank.tga', color = self.barColour)
        bar.setTransparency(1)
        
        if self.simulateData:
            # initialising perlin noise generator
            perlin = PerlinNoise2(1, 1)
            perlinCount = 0
            
        self.buffer = [(self.inputRange[1] - self.inputRange[0]) / 2] * self.bufferLength
            
        while True:
            if self.simulateData:
                # simulating input
                self.bci = perlin.noise(perlinCount)
                self.bci = self.map(self.bci, [-1, 1], self.inputRange)
                perlinCount += self.perlinStepSize
                
            if self.useThresholds and self.bci < self.bciThresholds[0] or self.bci > self.bciThresholds[1]:
                # appending input only if it is beyond the thresholds
                self.buffer.append(self.bci)
                self.buffer = self.buffer[1:]
            elif not self.useThresholds:
                # always appending input
                self.buffer.append(self.bci)
                self.buffer = self.buffer[1:]
            
            # taking buffer mean as current value
            currentValue = sum(self.buffer) / len(self.buffer)
                
            # redrawing bar
            if self.centreVertical:
                maxHeight = (self.barHeight - 4 * self.frameWidth) / 2
                currentBarHeight = self.map(currentValue, self.inputRange, [-maxHeight, maxHeight])
                bar.setScale(self.barWidth - 4 * self.frameWidth, 0, currentBarHeight)
                bar.setPos((0, 0, currentBarHeight))
            else:
                maxHeight = self.barHeight - 4 * self.frameWidth
                currentBarHeight = self.map(currentValue, self.inputRange, [0, maxHeight])                
                bar.setScale(self.barWidth - 4 * self.frameWidth, 0, currentBarHeight)
                bar.setPos((0, 0, -self.barHeight + 4 * self.frameWidth + currentBarHeight))
            
            self.sleep(1.0 / self.fps)
        
        
    def exit(self):
        print "Exiting..."
        exit()
        