"""
Downloads anime themes from animethemes.moe. Supports Batch download and animelist connecting.
"""
from .downloader import *
from .errors import *
from .options import DEFAULT, OPTIONS, setOptions
from .parsers import *

from .tools import init_logger
init_logger()
del init_logger
