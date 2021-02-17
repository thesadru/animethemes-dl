"""
Models for animethemes-dl.
Uses TypedDict to add hinting while still using builtin data types.
"""
import sys
if sys.version_info >= (3,9):
    from .animelist import *
    from .animethemes import *
    from .dldata import *
    from .options import Options
else: # in case older python version is downloaded
    from typing import Any
    __getattr__ = lambda _: Any

del sys
