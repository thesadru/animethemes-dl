import time
from os import PathLike, makedirs, mkdir
from os.path import getmtime, isdir, isfile, join
from tempfile import gettempdir

from ..options import OPTIONS

TEMPDIR = join(gettempdir(), 'animethemes-dl')
DLCACHEDIR = join(TEMPDIR, 'dlchache')
if not isdir(TEMPDIR): makedirs(TEMPDIR)
if not isdir(DLCACHEDIR): mkdir(DLCACHEDIR)

def get_tempfile_path(file: str) -> PathLike:
    return join(TEMPDIR, file)

def cache_is_young_enough(path: PathLike) -> bool:
    return isfile(path) and time.time()-getmtime(path) <= OPTIONS['download']['max_cache_age']
