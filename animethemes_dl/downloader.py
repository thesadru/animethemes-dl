import logging
from logging import Logger
import tempfile
from os import makedirs, remove
from os.path import basename, isfile, join, realpath, splitext

from pySmartDL import SmartDL, utils

from animethemes_dl.options import OPTIONS, setOptions

from .tools import add_id3_metadata, ffmpeg_convert, fix_faulty_url
from .errors import BadThemesUrl
from .parsers import get_download_data
from .models import ADownloadData,DownloadData

logger = logging.getLogger(__name__)

# optimization
utils.is_HTTPRange_supported = lambda *_,**__: False
tempdir = join(tempfile.gettempdir(),'pySmartDL')

def download_theme(data: ADownloadData):
    """
    Downloads a theme with theme `data`.
    Uses two destinations for audio and video folders.
    Adds metadata for audio files.
    """
    # what files are requested
    video,audio = data['video_path'],data['audio_path']
    # what files exists
    if video is None:
        video = realpath(join(tempdir,splitext(basename(audio))[0]+'.webm'))
    will_delete_video = video is None
    exvideo = isfile(video) if video else None
    exaudio = isfile(audio) if audio else None
    # what files are needed to be downloaded
    redownload = not OPTIONS['download']['no_redownload']
    # needed if         can download        and       requested
    needaudio = (redownload or not exaudio) and audio
    needvideo = (redownload or not exvideo) and (video or needaudio)
    
    if needvideo:
        if will_delete_video:
            dest = None
        else:
            dest = video
        obj = SmartDL(
            data['url'],
            dest,
            progress_bar=not OPTIONS['quiet'],
            # logger=logger.root,
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
        print(obj.get_dl_size())
        if obj.get_dl_size() <= 0x100000: # less than MB probably means a faulty url
            data['url'] = fix_faulty_url(data)
            remove(obj.get_dest())
            download_theme(data) # I gave up and made the function recursive
        
        video = obj.get_dest()
        exvideo = True
    else:
        exvideo = False
    
    if needaudio:
        try:
            ffmpeg_convert(video,audio)
        except KeyboardInterrupt as e:
            quit(e)
        add_id3_metadata(audio,data['metadata'],OPTIONS['download']['add_coverart'])
    
    if video and exvideo and will_delete_video:
        remove(video)

def batch_download_themes(data: DownloadData):
    """
    Batch downloads all a list of `dl_data`.
    """
    for path in (OPTIONS['download']['audio_folder'],OPTIONS['download']['video_folder']):
        try: 
            if path:
                makedirs(path)
        except FileExistsError:
            pass
    
    for index,theme in enumerate(data,1):
        logger.info(f"Downloading \"{theme['metadata']['album']} | {theme['metadata']['title']}\" (#{index})")
        
        for i in range(OPTIONS['download']['retries']):
            try:
                download_theme(theme)
            except BadThemesUrl:
                break
            except Exception as e:
                logger.info('fucked up, retrying...')
                logger.exception(e)
            else:
                break

def batch_download(options: dict={}):
    """
    Takes in options that will be passed into `setOptions`.
    Downloads all themes and adds metadata to it.
    Basically the main function of `batch_download`.
    """
    setOptions(options)
    logger.info('initializing animethemes-dl')
    data = get_download_data(
        OPTIONS['animelist']['username'],
        OPTIONS['animelist']['anilist'],
        OPTIONS['animelist']['animelist_args']
    )
    batch_download_themes(data)
    logger.info('finished downloading')

if __name__ == '__main__':
    import sys
    logging.basicConfig(
        level=logging.DEBUG if len(sys.argv)==3 else logging.INFO,
        format='%(message)s'
    )
    batch_download({
        'animelist':{
            'username':'sadru',
            'minscore':9,
            'minpriority':2
        },
        'filter':{
            'spoilers':False
        },
        'download':{
            'audio_folder':'test/anime_themes',
            'video_folder':'test/anime_themes/video',
            'no_redownload':True,
            'add_coverart':True,
            'sort':lambda x:x['animelist']['title']
        },
        # 'ffmpeg':'./ffmpeg.exe'
    })
