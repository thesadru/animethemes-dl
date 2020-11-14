"""
Does general repair for animethemes-dl. This is mostly for updating
"""
import logging
from os import PathLike, listdir, remove
from os.path import isfile,join
from typing import Set

from ..models import DownloadData
from ..options import OPTIONS
from .audio import add_id3_metadata


def update_metadata(data: DownloadData):
    """
    Updates metadata for all mp3's
    """
    for anime in data:
        path = anime['audio_path']
        if path is not None and isfile(path):
            logger.info(f'[tag] readding metadata for {path}')
            add_id3_metadata(
                path,
                anime['metadata'],
                OPTIONS['download']['add_coverart']
            )

def delete_unwanted(wanted: Set[PathLike], folder: PathLike):
    """
    Deletes all Unwanted files in a folder.
    """
    for path in listdir(folder):
        path = join(folder,path)
        if path not in wanted:
            remove(path)
            logger.info(f'[delete] Deleting {path}')

def delete_all_unwanted(data: DownloadData, video: bool=True, audio:bool=True):
    """
    Deletes all unwanted files with DownloadData.
    Choose which type to delete.
    """
    video = video and OPTIONS['download']['video_folder']
    audio = video and OPTIONS['download']['audio_folder']

    videopaths,audiopaths = set(),set()
    for i in data:
        videopaths.add(i['video_path'])
        audiopaths.add(i['audio_path'])
    
    if video: delete_unwanted(videopaths,OPTIONS['download']['video_folder'])
    if audio: delete_unwanted(audiopaths,OPTIONS['download']['audio_folder'])

def repair(data: DownloadData):
    """
    Deletes unwanted files and updates metadata
    """
    delete_all_unwanted(data)
    update_metadata(data)

if __name__ == "__main__":
    from ..parsers import get_download_data
    from ..options import setOptions
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    setOptions({
        'download':{
            'audio_folder':'test/anime_themes/audio',
            'add_coverart':True,
            'coverart_folder':'test/anime_themes/coverarts'
        }
    })
    repair(get_download_data('sadru'))
