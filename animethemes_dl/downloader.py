"""
Download files with DownloadData.
"""
import logging
from os import PathLike, makedirs, remove
from os.path import isfile
from typing import Tuple, List

from pySmartDL import SmartDL, utils

from animethemes_dl.options import OPTIONS, setOptions

from .errors import BadThemesUrl
from .models import DownloadData, Options
from .parsers import get_download_data
from .tools import add_id3_metadata, compress_files, ffmpeg_convert, fix_faulty_url

logger = logging.getLogger('animethemes-dl')

# optimization
utils.is_HTTPRange_supported = lambda *_,**__: False

def determine_needed(video: PathLike=None, audio: PathLike=None) -> Tuple[bool,bool]:
    """
    Check what files need to be downloaded.
    """
    # what files exists
    exvideo = isfile(video) if video else None
    exaudio = isfile(audio) if audio else None
    # what files are needed to be downloaded
    redownload = not OPTIONS['download']['no_redownload']
    # needed if         can download        and     requested
    needaudio = (redownload or not exaudio) and audio
    needvideo = (redownload or not exvideo) and (video or needaudio)
    return needvideo,needaudio

def download_video(data: DownloadData, use_temp: bool=False):
    """
    Downloads a video with data.
    Returns destination
    """
    if use_temp:
        dest = None
    else:
        dest = data['video_path']
    
    logger.debug(f'downloading to {dest}')
    
    obj = SmartDL(
        data['url'],
        dest,
        progress_bar=not OPTIONS['quiet'],
        # logger=logger.root,
        timeout=OPTIONS['download']['timeout'],
        verify=False
    )
    try:
        obj.start()
    except Exception as e:
        obj.stop()
        logger.error(str(e))
    except KeyboardInterrupt as e:
        obj.stop()
        quit(e)
    
    dest = obj.get_dest()
    
    if obj.get_dl_size() <= 0x100000: # less than MB probably means a faulty url
        data['url'] = fix_faulty_url(data)
        if dest and isfile(dest):
            remove(dest)
        download_theme(data) # I gave up and made the function recursive
    
    return dest

def convert_audio(data: DownloadData, video_path: PathLike=None):
    """
    Converts webm video into audio and adds metadata.
    Can force a different video path.
    """
    data['video_path'] = data['video_path'] or video_path
    try:
        ffmpeg_convert(data['video_path'],data['audio_path'])
    except KeyboardInterrupt as e:
        # delete unfinished ffmpeg conversions
        if isfile(data['audio_path']):
            remove(data['audio_path'])
        quit(e)
    add_id3_metadata(data['audio_path'],data['metadata'],data['info']['malid'])

def download_theme(data: DownloadData, dlvideo: bool=True, dlaudio:bool=True):
    """
    Downloads a theme with theme `data`.
    Uses two destinations for audio and video folders.
    You can choose which files you want to download.
    Adds metadata for audio files.
    """
    if dlvideo:
        video_path = download_video(data,data['video_path'] is None)
    else:
        video_path = None
    
    if dlaudio:
        convert_audio(data,video_path)
    
    #if   downloaded video    and     didn't save video
    if video_path is not None and data['video_path'] is None:
        logger.debug(f'removing {video_path}')
        remove(video_path)

def batch_download_themes(data: List[DownloadData]):
    """
    Batch downloads all a list of `dl_data`.
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
    
    for index,theme in enumerate(data,1):
        dlvideo,dlaudio = determine_needed(theme['video_path'],theme['audio_path'])
        if not (dlvideo or dlaudio):
            continue
        
        logger.info(f"[download] \"{theme['metadata']['disc']} | {theme['metadata']['title']}\" (#{index})")
        
        for retry in range(1,OPTIONS['download']['retries']):
            try:
                download_theme(theme,dlvideo,dlaudio)
            except BadThemesUrl:
                break
            except Exception as e:
                logger.info(f'[error] fucked up, retrying ({retry})...')
                logger.exception(e)
            else:
                break

def batch_download(options: dict=Options):
    """
    Takes in options that will be passed into `setOptions`.
    Downloads all themes and adds metadata to it.
    Basically the main function of `batch_download`.
    """
    setOptions(options)
    logger.info('[progress] initializing animethemes-dl')
    data = get_download_data(
        OPTIONS['animelist']['username'],
        OPTIONS['animelist']['anilist'],
        OPTIONS['animelist']['animelist_args']
    )
    batch_download_themes(data)
    logger.info('[progress] finished downloading')
    
    if OPTIONS['download']['compression']['root_dir']:
        compress_files(**OPTIONS['download']['compression'])

if __name__ == '__main__':
    logging.basicConfig(
        format='%(message)s'
    )
    logger.setLevel(logging.DEBUG)
    batch_download({
        'animelist':{
            'username':'sadru',
            'minscore':9,
            'minpriority':2
        },
        'filter':{
            'entry': {
                'spoiler':False
            }
        },
        'download':{
            'audio_folder':'anime_themes/audio',
            'video_folder':'anime_themes/video',
            'no_redownload':True,
            'coverart': {
                'resolution': 3,
                'folder': 'anime_themes/coverarts'
            },
            'timeout':15
        },
        # 'ffmpeg':'./ffmpeg.exe'
    })
