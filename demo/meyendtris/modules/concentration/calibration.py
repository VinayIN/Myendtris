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
from random import random
from time import time
import math
import sys
import colorsys

from meyendtris.framework.latentmodule import LatentModule
from direct.showbase.ShowBase import ShowBase


class DistractionCalibration(LatentModule):
    def __init__(self):
        super().__init__()
    
    def move_blocks(self):
        self.write("hello", duration=10)

    def run(self):
        self.move_blocks()
        

# Make an instance of our class and run the demo
viewer = DistractionCalibration()
viewer.start()
