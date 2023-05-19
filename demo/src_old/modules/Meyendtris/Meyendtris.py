# -*- coding: utf-8 -*-

"""
@author     Laurens R Krol, Sarah-Christin Freytag
@org        Team PhyPA, Technische Universitaet Berlin
@date       2016-10-09
"""

"""
"Meyendtris" is a variant of Tetris where the regular game mechanics (moving, rotating, and dropping the tetrominoes) are controlled by eye gaze. In addition, two passive BCIs influence additional parameters:

1. The game speed depends on the player's relaxation and focus: the more distracted the player is, the faster and more difficult the game will be. 
2. An error detection mechanism is proposed to remove erroneously placed tetrominoes. When an error-related potential is detected following a tetromino drop, this tetromino is removed from the field.

The first point means that players should not let their mistakes upset them -- it'll lead to only more mistakes. They should try to relax. At the same time however, the second point should work best when the player is properly focused. Eye tracking ideally removes the game's dependency on manual input, which is often a bottleneck in original Tetris (increasingly so with increasing game speed). In Meyendtris, the game thus becomes a battle against oneself, balancing two mental states.

Publication:

    Krol, L. R., Freytag, S.-C., & Zander, T. O. (2017). Meyendtris: A hands-free, multimodal Tetris clone using eye tracking and passive BCI for intuitive neuroadaptive gaming. In Proceedings of the 19th ACM International Conference on Multimodal Interaction (pp. 433–437). New York, NY, USA: ACM. doi: 10.1145/3136755.3136805

The error detection mechanism is not currently implemented, but "simulated" using the self.undoProbability variable, which simply randomly decides whether or not to remove a dropped tetromino.

To set up, make sure either a gaze or a cursor position LSL stream is available and that the width of the SNAP window equals the width of the screen, in pixels. This can be configured in src/studies/meyendtrisdisplaysettings.prc. The height of the window can also be adjusted there. Note that some eye trackers may not function if the SNAP window fills the entire screen. In that case, a window height slightly smaller than the screen height can be given.

For game speed adaptation, a value between 1 and 2 must be written to self.bci. This value represents the user's current relaxation. SNAP allows this to be done through TCP by sending the string 'setup self.bci=1.5' (or any other number) to port 7897 of the computer on which SNAP is running (unless another port has been set). BCILAB has a built-in function to communicate with SNAP.

The size of the blocks can be varied to correspond to the eye tracker's accuracy. This is done by changing the number of rows in the playing field (self.rows). The block size will adjust automatically to fill the screen height.

This game is meant to be played hands-free. This file includes mouse and manual control for testing purposes. Note that manual downward control can lead to clearLines() or spawnTetromino() to be called during an undoAnimation, clearing the entire field, or ending the game. Use space to directly drop the tetrominoes instead.

Meyendtris was developed during the IEEE Brain Hackathon in Budapest on October 8th and October 9th, 2016. Team PhyPA was sponsored at this event by Brain Products GmbH.

To-do:
- Do not continuously change the music play rate, since doing this can make it sound like a dying cat. Instead, only change the speed every x seconds or so?
- Prevent rotation to happen more than once without gaze leaving the rotation field. This will allow faster rotation times without additional accidental rotations.
- Implement dual rotation: instead of looking up, look left/right of the playing field to rotate the block counter/clockwise.
- Better tetromino rotation: rotate around a central point rather than just flipping the matrix (or have an additional left/right adjustment parameter to be applied after rotation). Also, perhaps allow tetrominos to be rotated even when they're at the very edge of the field. Currently, this doesn't work as the rotation collides with the field edges.
- Better column highlighting/tetromino positioning: position tetromino's centre or lowermost block at the selected column, not its leftmost block.
- Optional auto block size setting: show a single block in the centre that should be gazed at. Start with smallest. If cursor remains within that block for x% of samples in y seconds, use that block size for the game.
- Implement error detection mechanism. Easiest way should be: Instead of "if random() < self.undoProbability: self.undoTetromino()", wait for a bit after landing a block to receive error classifier output, then call self.undoTetromino() when positive. 
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


from ctypes import windll
from direct.gui.DirectGui import DirectEntry
from framework.latentmodule import LatentModule
from pylsl.pylsl import stream_inlet, resolve_stream, resolve_streams, vectorf
from random import choice, random
from time import time

class Main(LatentModule):
    def __init__(self):
        LatentModule.__init__(self)

        self.backgroundColour = (0, 0, 0, 1)    # background colour
        self.fps = 60                           # frames per second

        self.bciBufferLength = 120              # number of samples to take the mean of (collects 1 sample per frame)

        self.musicFile = "tetris.mp3"           # music file; playback speed will be scaled by BCI output
        self.musicPlayRateRange = [1.5, 0.75]   # playback speed range in # times normal speed [fastest, slowest]
        self.moveTimeRange = [.4, 1.5]          # game speed range in seconds per step, also scaled by BCI output [fastest, slowest]
        self.undoProbability = 0.00             # probability that a tetromino drop will be undone (to be replaced by ERP-based undo)

        self.rows = 17                          # playing field configuration
        self.cols = 10

        self.rotationRows = 4                   # number of upper rows to use as rotation area

        # eyetracking vars
        self.showGaze = True                    # whether or not to show current gaze location
        self._colOffset = 10                    # horizontal margin in pixels (column border margins will be ignored)
        self.columnDwellTime = 5                # dwell time in frames for column selections
        self.dropDwellTime = 300                # dwell time in frames for tetromino drops
        self.rotationDwellTime = 60             # dwell time in frames for tetromino rotations
        
        self.mapDwellTimes = True               # whether or not to also adjust dwell times based on BCI input
        self.columnDwellTimeRange = [5, 5]      # [fastest, slowest]
        self.dropDwellTimeRange = [100, 300]
        self.rotationDwellTimeRange = [30, 120]

        self.tetrominoes = [                    # tetromino shapes; different numbers represent different colours
                        [[0,1,0],
                         [1,1,1]],

                        [[2,0],
                         [2,0],
                         [2,2]],

                        [[0,3],
                         [0,3],
                         [3,3]],

                        [[4,4],
                         [4,4]],

                        [[5,5,0],
                         [0,5,5]],

                        [[0,6,6],
                         [6,6,0]],

                        [[7],
                         [7],
                         [7],
                         [7]]
                ]

        self.colours = [ (53/255.0, 115/255.0, 226/255.0, .9),      # the colours of the seven tetrominos;
                         (226/255.0, 65/255.0, 7/255.0, .9),        # the last colour is for the error animation
                         (104/255.0, 177/255.0, 8/255.0, .9),
                         (206/255.0, 53/255.0, 45/255.0, .9),
                         (154/255.0, 40/255.0, 225/255.0, .9),
                         (180/255.0, 180/255.0, 180/255.0, .9),
                         (227/255.0, 118/255.0, 27/255.0, 1),
                         (0.5, 0, 0, 1) ]
        

    def waitForUser(self):
        # waiting for user to be ready
        self.write(
                text = "Press enter to continue",
                fg = (.5, .5, .5, 1),
                bg = ( 0,  0,  0,  .5),
                duration = "enter")


    def get_gazeData(self):
        if self.inlet:
            # getting current x, y position in pixels
            sample = vectorf()
            while self.inlet.pull_sample(sample, 0.0):
                self._gazeX = list(sample)[self.inletXpos]
                self._gazeY = list(sample)[self.inletYpos]

            if self.showGaze and self._gazeX and self._gazeY:
                self.highlightPixel(self._gazeX, self._gazeY)


    def run(self):
        # finding stream
        self.inlet = None
        streams = list(resolve_streams(1.0))
        try:
            # first trying to find a gaze stream
            stream = next(s for s in streams if s.type() == 'Gaze')
            print "Found gaze stream", stream.name(), "from", stream.hostname()
            self.inlet = stream_inlet(stream)
            self.inletXpos = 0  # index of x screen position in each sample
            self.inletYpos = 1  # index of y screen position in each sample
        except:
            try:
                # if no gaze stream is available, trying to find a cursor position stream.
                # most eye trackers allow the tracker to take control over the cursor, thus
                # bypassing the requirement for LSL support by the tracker. this does
                # require the LSL Mouse Connector to be running.
                stream = next(s for s in streams if s.type() == 'Position')
                print "Found position stream", stream.name(), "from", stream.hostname()
                self.inlet = stream_inlet(stream)
                self.inletXpos = 0
                self.inletYpos = 1
            except:
                # fallback: manual control
                print "No stream found: manual control"
                self.showGaze = False
                self.accept("arrow_left", self.moveTetromino, [0, -1])
                self.accept("arrow_right", self.moveTetromino, [0, 1])
                self.accept("arrow_down", self.moveTetromino, [1, 0])
                self.accept("arrow_up", self.rotateTetromino)
                self.accept("1", self.setSelectedColumn, [0])
                self.accept("2", self.setSelectedColumn, [1])
                self.accept("3", self.setSelectedColumn, [2])
                self.accept("4", self.setSelectedColumn, [3])
                self.accept("5", self.setSelectedColumn, [4])
                self.accept("6", self.setSelectedColumn, [5])
                self.accept("7", self.setSelectedColumn, [6])
                self.accept("8", self.setSelectedColumn, [7])
                self.accept("9", self.setSelectedColumn, [8])
                self.accept("0", self.setSelectedColumn, [9])
                self.accept("space", self.dropTetromino)
                
        # setting background colour
        base.win.setClearColor(self.backgroundColour)
        
        self.waitForUser()

        # initial values
        self.blockSize = 2.0 / self.rows
        self.bci = 1.5
        self.bciBuffer = [self.bci] * self.bciBufferLength
        self.undoAnimation = False
        self._currentSampleCol = -1
        self._currentSelectedCol = -1
        self._gazeX = None
        self._gazeY = None
        self._lastCol = None
        self.pickedColumn = False
        self.gazeDwellTimeList = []
        self.inRotationArea = False
        self.rotateTimeList = []

        # generating game field array
        self.field = [[0 for i in range(self.cols)] for j in range(self.rows)]
        self.initialiseFieldGraphics()

        # getting column boundaries in pixels
        self.screensize = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)
        farLeft = -(self.cols * self.blockSize) / 2.0
        self.columnBoundaries = [[farLeft + (self.blockSize * col), farLeft + (self.blockSize * (col + 1))] for col in range(self.cols)]
        for col in range(self.cols):
            for boundary in range(2):
                self.columnBoundaries[col][boundary] = int(self.map(
                        self.columnBoundaries[col][boundary],
                        [-base.getAspectRatio(), base.getAspectRatio()],
                        [0, self.screensize[0]]))

        # generating rotation area
        rotationPart = (4 * self.blockSize) / 2.0
        self.rotationArea = self.screensize[1] * rotationPart
        self.rotationAreaBoundaryGraphics = self.rectangle(
                (farLeft, -farLeft, 1, 1 - (2.0 * rotationPart)),
                color = (1, 1, 1, .1),
                duration = 0)
        self.rotationAreaBoundaryGraphics.configure( color = (1, 1, 1, .1 ))

        if self.showGaze:
            self.pixel = self.rectangle((10, 10.01, 10, 10.01),  color = (1,1,1,1), duration = 0)

        # initialising music
        self.music = base.loader.loadSfx(self.musicFile)
        self.music.setLoop(True)
        self.music.play()

        # accepting keyboard input
        self.accept("b", self.toggleBCI)

        # starting game: spawning first tetromino
        self.spawnTetromino()

        # entering game loop
        lastFrameTime = time()
        lastMoveTime = time()

        while True:
            # getting current values
            self.updateBCI()
            self.get_gazeData()
            self.check_RotationArea()
            self.check_Columns()

            # adjusting dependent values
            self.music.setPlayRate(self.map(self.currentBCI, [1, 2], self.musicPlayRateRange))
            if not self.inRotationArea: self.rotationAreaBoundaryGraphics.configure( color = (1, 1, 1, .1 ))
            else: self.rotationAreaBoundaryGraphics.configure( color = (1, 1, 1, .25))
            if self.mapDwellTimes:
                self.columnDwellTime = self.map(self.currentBCI, [1, 2], self.columnDwellTimeRange)
                self.dropDwellTime = self.map(self.currentBCI, [1, 2], self.dropDwellTimeRange)
                self.rotationDwellTime = self.map(self.currentBCI, [1, 2], self.rotationDwellTimeRange)

            # handling those actions that happen at game speed intervals
            currentMoveTime = self.map(self.currentBCI, [1, 2], self.moveTimeRange)
            if time() - lastMoveTime > currentMoveTime:
                if self.undoAnimation:
                    self.undoTetromino()
                else:
                    self.moveTetromino(1, 0)
                lastMoveTime = time()

            self.updateFieldGraphics()

            self.sleep(1.0 / self.fps - (time() - lastFrameTime))
            lastFrameTime = time()


    def setSelectedColumn(self, col):
        # changing currently selected column, and corresponding tetromino position
        self._currentSelectedCol = col
        self.positionTetronimo(col)


    def updateBCI(self):
        # updating current BCI buffer and mean value
        self.bciBuffer.append(self.bci)
        self.bciBuffer = self.bciBuffer[1:]
        self.currentBCI = sum(self.bciBuffer) / float(len(self.bciBuffer))


    def spawnTetromino(self):
        # spawning random tetromino at top middle of the field
        self.currentTetromino = choice(self.tetrominoes)
        self.currentTetrominoTopLeft = [0, self.cols / 2 - len(self.currentTetromino[0]) / 2]

        # resetting dwell times
        self.resetGaze()

        # ending game if there's no room for the selected tetromino
        if self.collision(self.currentTetrominoTopLeft):
            self.restartGame()


    def moveTetromino(self, down, right):
        # moving tetromino if no collision is detected at the indicated position;
        # landing tetromino if a downward motion caused a colision
        newTopLeft = [self.currentTetrominoTopLeft[0] + down, self.currentTetrominoTopLeft[1] + right]

        if down > 0 and self.collision(newTopLeft):
            self.landTetromino()
        elif not self.collision(newTopLeft):
            self.currentTetrominoTopLeft[0] += down
            self.currentTetrominoTopLeft[1] += right

    def dropTetromino(self):
        # dropping tetromino by moving it downwards until it collides
        while not self.collision([self.currentTetrominoTopLeft[0]+1, self.currentTetrominoTopLeft[1]]):
            self.moveTetromino(1,0)

        self.landTetromino()


    def positionTetronimo(self, column):
        # moving tetromino horizontally towards selected column
        # (in steps of one, because collision detection must happen at every step)
        diff = self.currentTetrominoTopLeft[1] - column
        if diff > 0:
            for m in range(diff):
                self.moveTetromino(0, -1)
        elif diff < 0:
            for m in range(abs(diff)):
                self.moveTetromino(0, 1)


    def rotateTetromino(self):
        # rotating tetromino if no collision is caused
        newShape = [list(i) for i in zip(*self.currentTetromino[::-1])]
        if not self.collision(self.currentTetrominoTopLeft, newShape):
            self.currentTetromino = newShape


    def collision(self, newTopLeft, newShape = None):
        # checking if the current tetromino at a newly indicated position, or
        # a given tetromino shape at a given position, causes a collision,
        # i.e. whether or not any blocks overlap with already-landed blocks
        if newShape == None: newShape = self.currentTetromino
        for row in range(len(newShape)):
            for col in range(len(newShape[0])):
                if not newShape[row][col] == 0:
                    if newTopLeft[0]+row < 0 or newTopLeft[0]+row >= self.rows or newTopLeft[1]+col < 0 or newTopLeft[1]+col >= self.cols:
                        return True
                    elif not self.field[newTopLeft[0] + row][newTopLeft[1] + col] == 0:
                        return True

        return False


    def landTetromino(self):
        if random() < self.undoProbability:
            # removing tetromino if error detected
            self.undoTetromino()
        else:
            # adding tetromino to game field array
            for row in range(len(self.currentTetromino)):
                for col in range(len(self.currentTetromino[0])):
                    if not self.currentTetromino[row][col] == 0:
                        self.field[self.currentTetrominoTopLeft[0]+row][self.currentTetrominoTopLeft[1]+col] = self.currentTetromino[row][col]

            self.clearLines()
            self.spawnTetromino()


    def undoTetromino(self):
        # removing landed tetromino
        # this method is called twice: once to start the animation (highlighting the field),
        # once more to end the animation and spawn a new tetromino
        if not self.undoAnimation:
            # highlighting all empty field blocks
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.field[row][col] == 0:
                        self.field[row][col] = 8
            self.undoAnimation = True
        else:
            # reverting highlight, spawning new tetromino
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.field[row][col] == 8:
                        self.field[row][col] = 0
            self.undoAnimation = False
            self.spawnTetromino()
            
            
    def restartGame(self):
        self.updateFieldGraphics()
        self.waitForUser()
        
        # resetting game field
        for row in range(self.rows):
            for col in range(self.cols):
                self.field[row][col] = 0
                
        self.updateFieldGraphics()
        
        self.spawnTetromino()
        

    def clearLines(self):
        # checking for full horizontal rows
        for row in range(self.rows):
            if all(col > 0 for col in self.field[row]):
                for r in range(row, -1, -1):
                    self.field[r] = self.field[r-1][:]
                self.field[0] = [0] * self.cols


    def initialiseFieldGraphics(self):
        # drawing a rectangle for each element in the field array,
        # adding these to a fieldGraphics array

        self.fieldGraphics = []

        farLeft = -(self.cols * self.blockSize) / 2.0
        farTop = (self.rows * self.blockSize) / 2.0

        for row in range(self.rows):
            rowGraphics = []
            for col in range(self.cols):
                rowGraphics.append(
                        self.rectangle(
                                (
                                        farLeft + (self.blockSize * col),
                                        farLeft + (self.blockSize * (col + 1)),
                                        farTop - (self.blockSize * row),
                                        farTop - (self.blockSize * (row + 1))
                                ),
                                color = (.1,.1,.1,1),
                                duration = 0))
            self.fieldGraphics.append(rowGraphics)

        # drawing transparent white, somewhat smaller blocks on top of the field
        # for a bit of a 3D effect
        self.overlayGraphics = []
        margin = self.blockSize / 10.0
        for row in range(self.rows):
            rowGraphics = []
            for col in range(self.cols):
                rowGraphics.append(
                        self.rectangle(
                                (
                                        farLeft + (self.blockSize * col) + margin,
                                        farLeft + (self.blockSize * (col + 1)) - margin,
                                        farTop - (self.blockSize * row) - margin,
                                        farTop - (self.blockSize * (row + 1) - margin)
                                ),
                                color = (1,1,1,.1),
                                duration = 0))
            self.overlayGraphics.append(rowGraphics)


    def updateFieldGraphics(self):
        # drawing the field
        for row in range(self.rows):
            for col in range(self.cols):
                if self.field[row][col] == 0:
                    self.fieldGraphics[row][col].configure(color = (.1, .1, .1, 1))
                else:
                    self.fieldGraphics[row][col].configure(color = self.colours[self.field[row][col]-1])

        # drawing the current tetromino
        for row in range(len(self.currentTetromino)):
            for col in range(len(self.currentTetromino[0])):
                drawrow = row + self.currentTetrominoTopLeft[0]
                drawcol = col + self.currentTetrominoTopLeft[1]
                if not self.currentTetromino[row][col] == 0:
                    self.fieldGraphics[drawrow][drawcol].configure(color = self.colours[self.currentTetromino[row][col]-1])

        # highlighting currently selected column using the overlay graphics
        if not self._currentSelectedCol == -1:
            for row in range(self.rows):
                for col in range(self.cols):
                    if col == self._currentSelectedCol:
                        self.overlayGraphics[row][col].configure(color = (1,1,1,.25))
                    else:
                        self.overlayGraphics[row][col].configure(color = (1,1,1,.1))


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


    def toggleBCI(self):
        # for testing purposes: switching BCI value between maximum and minimum
        if self.bci == 2:
            self.bci = 1
        else:
            self.bci = 2


    def highlightPixel(self, x, y):
        # drawing a cursor at given pixel coordinates
        x = self.map(x, [0, self.screensize[0]], [-base.getAspectRatio(), base.getAspectRatio()])
        y = self.map(y, [0, self.screensize[1]], [1, -1])
        self.pixel.configure( pos = (x, 0, y) )


    #eye
    def check_RotationArea(self):
        if self._gazeY and self._gazeY < self.rotationArea:
            self.rotateTimeList.append(self._gazeY)
            self.inRotationArea = True

            if len(self.rotateTimeList) > self.rotationDwellTime:
                self.rotateTetromino()
                self.rotateTimeList = []
                self.inRotationArea = False

        else:
            self.inRotationArea = False
            self.rotateTimeList = []


    def check_Columns(self):
            self._lastCol = self._currentSampleCol
            self.pickedColumn = False

            for col in range(self.cols): #0-9
                if self._gazeX > self.columnBoundaries[col][0] + self._colOffset and self._gazeX < self.columnBoundaries[col][1] - self._colOffset:
                    self._currentSampleCol = col
                    self.pickedColumn = True
                    #print(self._currentSampleCol)

            if self._currentSampleCol == self._lastCol and self._currentSampleCol != -1 and self.inRotationArea == False:
                 self.gazeDwellTimeList.append(self._gazeX)
                 if len(self.gazeDwellTimeList) > self.columnDwellTime: #random upper limit, has to be tested
                    self.setSelectedColumn(self._currentSampleCol)
                     # self.positionTetronimo(self._currentSampleCol)

                 if len(self.gazeDwellTimeList) > self.dropDwellTime and self.inRotationArea == False:
                     self.dropTetromino()
                     self.gazeDwellTimeList = []

            else: self.gazeDwellTimeList = []


    def resetGaze(self):
        # resetting gaze buffers
        self.gazeDwellTimeList = []
        self.rotateTimeList = []

