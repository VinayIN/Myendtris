
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
import math
import sys
import colorsys

from meyendtris.framework.basicstimuli import BasicStimuli
from direct.showbase.ShowBase import ShowBase


class Main(BasicStimuli):
    def __init__(self):
        super().__init__()
    
    def start_calibration(self):
        # self.write("hello", duration=10)
        name1 = input("What is your NAME ? ")

        print("Best of Luck! ", name1)

        words1 = ['donkey', 'aeroplane', 'america', 'program',
                'python', 'language', 'cricket', 'football',
                'hockey', 'spaceship', 'bus', 'flight']

        # rdm.choice() function will choose one random word from the gven list of words
        word1 = rdm.choice(words1)

        print("Please guess the characters: ")

        guesses1 = ''

        # we can use any number of turns here
        turns1 = 10

        while turns1 > 0:

            # counting the number of times a user is failed to guess the right character
            failed1 = 0

            # all the characters from the input word will be taken one at a time.
            for char in word1:

                # here, we will comparing that input character with the character in guesses1
                if char in guesses1:
                    print(char)

                else:
                    print("_")

                    # for every failure of the user 1 will be incremented in failed1
                    failed1 += 1

            if failed1 == 0:
                # user will win the game if failure is 0 and 'User Win' will be given as output
                print("User Win")

                # this will print the correct word
                print("The correct word is: ", word1)
                break

                # if the user has input the wrong alphabet then
            # it will ask user to enter another alphabet
            guess1 = input("Guess another character:")

            # every input character will be stored in guesses
            guesses1 += guess1

            # here, it will check input with the character in word
            if guess1 not in word1:

                turns1 -= 1
                self.marker("error"+str(time.time))

                # if the input character doesnot match the word
                # then "Wrong Guess" will be given as output
                print("Wrong Guess")

                # this will print the number of turns left for the user
                print("You have ", + turns1, 'more guesses ')

                if turns1 == 0:
                    print("User Loose")

    def run(self):
        self.start_calibration()
