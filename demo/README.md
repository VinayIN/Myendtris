SNAP
====

Simulation and Neuroscience Application Platform

The Simulation and Neuroscience Application Platform (SNAP) is part of the ERICA real-time experimentation environment.
To install the runtime engine required to run SNAP and/or and editor, please follow the instructions in the file INSTALLATION NOTES.txt.
To learn programming with SNAP, please have a look at the file "LEARNING SNAP.TXT" in the src directory.

Happy experiment coding!


Installation
====
Install meyendtris to your system in editable mode. 
```bash
pip install -e .
```


## HOW TO RUN ANY `.py`?
#### 1. If installed as a package
It is possible to run any script from any directory.

Example is shown below:
```bash
# If calibration.py is the file you want to run
python -m meyendtris.modules.concentration.calibration
or
python /path_to_the_script.py
```


#### 2. If not installed as a package
cd into the folder `demo`.
**Important:** This should be your root path.

```bash
cd demo
```
We are considering, `meyendtris` as a package name. So if you also need to create a .ipynb notebook, create them all inside the root folder which is `demo`.

`import meyendtris` should now work as a package.

If you need to run a file as a script then use the `-m` tag in your python command.

Example is shown below:
```bash
# If calibration.py is the file you want to run
python -m meyendtris.modules.concentration.calibration

# If game.py is the file you want to run
python -m meyendtris.modules.game
```