
# Meyendtris v0.1.1 

Meyendtris is a variant of Tetris where the regular game mechanics (moving, rotating, and dropping the tetrominoes) are controlled by eye gaze. In addition, two passive BCIs influence additional parameters:

1. The game speed depends on the player's relaxation and focus: the more distracted the player is, the faster and more difficult the game will be. 
2. An error detection mechanism is proposed to remove erroneously placed tetrominoes. When an error-related potential is detected following a tetromino drop, this tetromino is removed from the field. (Not currently implemented.)

The first point means that players should not let their mistakes upset them -- it'll lead to only more mistakes. They should try to relax. At the same time however, the second point should work best when the player is properly focused. Eye tracking ideally removes the game's dependency on manual input, which is often a bottleneck in original Tetris (increasingly so with increasing game speed). In Meyendtris, the game thus becomes a battle against oneself, balancing two mental states.

Meyendtris was developed during the IEEE Brain Hackathon in Budapest on October 8th and October 9th, 2016 by members of Team PhyPA: Laurens R Krol, Sarah-Christin Freytag, and Thorsten O Zander. Team PhyPA was sponsored at this event by Brain Products GmbH.



## Publication:

Krol, L. R., Freytag, S.-C., & Zander, T. O. (2017). Meyendtris: A hands-free, multimodal Tetris clone using eye tracking and passive BCI for intuitive neuroadaptive gaming. In Proceedings of the 19th ACM International Conference on Multimodal Interaction (pp. 433–437). New York, NY, USA: ACM. doi: 10.1145/3136755.3136805



## Requirements: 

Meyendtris has been implemented in SNAP, which is based on the Panda3D engine. First, install the Panda3D SDK, available from https://www.panda3d.org. Panda3D will come with its own version of Python, and an executable called ppython.exe. The Meyendtris launcher (see below) calls this executable to start Meyendtris. Thus, make sure ppython is in the search path, or adjust the launcher batch file.



## Usage:    

To start Meyendtris, launch ./demo/launcher-Meyendtris.bat and select the third option by typing "3" and pressing enter. It will search for an LSL gaze stream or, failing that, an LSL cursor position stream (as e.g. produced by the app in ./misc/Mouse). This latter option should thus work with any eye tracker that can assume control over the cursor. If no stream is found, Meyendtris reverts to manual control. 

Option 1 in the launcher menu presents a calibration paradigm, guiding participants through phases of relative cognitive load and relaxation. A trained classifier's output can be tested using the second option. 

Details can be found in the code of each module, located in ./demo/src/modules.
