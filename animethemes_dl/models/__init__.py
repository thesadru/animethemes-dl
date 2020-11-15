"""
Models for animethemes-dl.
Uses TypedDict to add hinting while still using builtin data types.
"""
from .animelist import RawAnimeList
from .animethemes import RawAnimeThemes
from .themes import Themes
from .dldata import ADownloadData,DownloadData,Metadata
from .literals import *
from .options import Options,_TAGS_TUPLES,_NOTE_TUPLES,DEFAULT