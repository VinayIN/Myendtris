import os
import pathlib
from direct.showbase.ShowBase import ShowBase


__BASE__ = ShowBase()
__PACKAGE_PATH__ = os.path.dirname(os.path.abspath(__file__))
__ROOT_PATH__ = os.path.dirname(os.path.abspath(__PACKAGE_PATH__))
__version__ = "0.2.0"

def path_join(path: str, parent=__ROOT_PATH__):
    full_path = os.path.abspath(os.path.join(parent, path.lstrip('/')))
    if os.path.exists(full_path):
        return full_path
    raise FileNotFoundError("Check your enter path, or enter a parent to join (available: __PACKAGE_PATH__, __ROOT_PATH__(default))")