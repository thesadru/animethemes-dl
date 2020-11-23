"""
Does general repair for animethemes-dl. This is mostly for updating.
"""
import logging
from os import PathLike, listdir, makedirs, remove
from os.path import isfile, join, realpath
from typing import List, Set

from ..models import DownloadData
from ..options import OPTIONS
from .audio import add_id3_metadata
from .compression import compress_files

logger = logging.getLogger('animethemes-dl')

def update_metadata(data: List[DownloadData], need_permission: bool=True) -> int:
    """
    Updates metadata for all mp3's.
    Returns amount of tagged files.
    """
    totag = []
    for anime in data:
        path = anime['audio_path']
        if path is not None and isfile(path):
            logger.debug(path)
            totag.append((path,anime['metadata'],anime['info']))
    
    if need_permission:
        answer = input(f'Tag {len(totag)} audio files? [y/n] ')
        if answer.lower() != 'y':
            return 0
    
    for path,metadata,info in totag:
        add_id3_metadata(path,metadata,info['malid'])
    
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
            logger.debug(path)
            todelete.append(path)
    
    if not todelete:
        return 0
    
    if need_permission:
        answer = input(f'Delete {len(todelete)} files from {folder}? [y/n] ')
        if answer.lower() != 'y':
            return 0
    
    for path in todelete:
        logger.info(f'[delete] Deleting {path}')
        remove(path)
    
    return len(todelete)

def delete_all_unwanted(data: List[DownloadData], video: bool=True, audio: bool=True, need_permission: bool=True):
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

def create_folders():
    """
    Generates all folders used by animethemes-dl.
    """
    for path in (
        OPTIONS['download']['audio_folder'],
        OPTIONS['download']['video_folder'],
        OPTIONS['download']['coverart']['folder']):
        try: 
            if path:
                makedirs(path)
        except FileExistsError:
            pass

def compress_directory(directory: PathLike):
        answer = input(f'Compress {directory}? [y/n] ')
        if answer.lower() == 'y':
            compress_files(**OPTIONS['download']['compression'])

def repair(data: List[DownloadData]):
    """
    Deletes unwanted files and updates metadata
    """
    create_folders()
    deleted = delete_all_unwanted(data,not OPTIONS['ignore_prompts'])
    tagged = update_metadata(data,not OPTIONS['ignore_prompts'])
    compress_dir = OPTIONS['download']['compression']['root_dir']
    if compress_dir:
        compress_directory(compress_dir)
    logger.info(f"[repair] deleted {deleted} files, retagged {tagged} audio files{', compressed dir.' if compress_dir else '.'}")

if __name__ == "__main__":
    from ..options import setOptions
    from ..parsers import get_download_data
    logger = logging.getLogger('animethemes-dl')
    logger.setLevel(logging.DEBUG)
    setOptions({
        'download':{
            'audio_folder': 'anime_themes/audio',
            'coverart': {
                'resolution': 3,
                'folder': 'anime_themes/coverarts'
            }
        }
    })
    repair(get_download_data('sadru'))
