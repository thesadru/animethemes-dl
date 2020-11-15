"""
Does general repair for animethemes-dl. This is mostly for updating
"""
import logging
from os import PathLike, listdir, remove
from os.path import isfile,join,realpath
from typing import Set

from ..models import DownloadData
from ..options import OPTIONS
from .audio import add_id3_metadata

logger = logging.getLogger('animethemes-dl')

def update_metadata(data: DownloadData, need_permission: bool=True) -> int:
    """
    Updates metadata for all mp3's.
    Returns amount of tagged files.
    """
    totag = []
    for anime in data:
        path = anime['audio_path']
        if path is not None and isfile(path):
            totag.append((path,anime['metadata']))
    
    if need_permission:
        answer = input(f'Tag {len(totag)} audio files? [y/n] ')
        if answer.lower() != 'y':
            return 0
    
    for path,metadata in totag:
        logger.info(f'[tag] readding metadata for {path}')
        add_id3_metadata(path,metadata,OPTIONS['download']['add_coverart'])
    
    return len(totag)

def delete_unwanted(wanted: Set[PathLike], folder: PathLike, need_permission: bool=True) -> int:
    """
    Deletes all Unwanted files in a folder.
    Returns amount of deleted files
    """
    todelete = []
    for path in listdir(folder):
        path = realpath(join(folder,path))
        if path not in wanted:
            todelete.append(path)
    
    if need_permission:
        answer = input(f'Delete {len(todelete)} files from {folder}? [y/n] ')
        if answer.lower() != 'y':
            return 0
    
    for path in todelete:
        logger.info(f'[delete] Deleting {path}')
        remove(path)
    
    return len(todelete)

def delete_all_unwanted(data: DownloadData, video: bool=True, audio: bool=True, need_permission: bool=True):
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
    
    total = 0
    if video: total+=delete_unwanted(videopaths,OPTIONS['download']['video_folder'],need_permission)
    if audio: total+=delete_unwanted(audiopaths,OPTIONS['download']['audio_folder'],need_permission)
    return total

def repair(data: DownloadData):
    """
    Deletes unwanted files and updates metadata
    """
    deleted = delete_all_unwanted(data,not OPTIONS['ignore_prompts'])
    tagged = update_metadata(data,not OPTIONS['ignore_prompts'])
    logger.info(f'[repair] deleted {deleted} files and retagged {tagged} audio files.')

if __name__ == "__main__":
    from ..parsers import get_download_data
    from ..options import setOptions
    logger = logging.getLogger('animethemes-dl')
    logging.basicConfig(level=logging.DEBUG)
    setOptions({
        'download':{
            'audio_folder':'test/anime_themes/audio',
            'add_coverart':True,
            'coverart_folder':'test/anime_themes/coverarts'
        }
    })
    repair(get_download_data('sadru'))
