"""
Compress files with shutil.make_archive().
"""
from os import PathLike
import shutil
import logging

logger = logging.getLogger('animethemes-dl')

def compress_files(base_name: str, format: str, root_dir: PathLike, base_dir: PathLike):
    """
    Compresses files with shutil.make_archive().
    """
    logger.info('[compress] started compression')
    shutil.make_archive(
        base_name,
        format,
        root_dir,
        base_dir,
        verbose=True,
        logger=logger
    )
    logger.info('[compress] finished compression')