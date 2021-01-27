"""
Options for animethemes_dl.
"""
import logging

from .models import Options

logger = logging.getLogger('animethemes-dl')
DEFAULT = {
    'animelist': {
        'username': '',
        'site': 'MyAnimeList',
        'animelist_args': {},
        'minpriority':0,
        'minscore':0,
        'range':[0,0]
    },
    'filter': {
        'smart': False,
        'no_copy': False,
        'spoiler': None,
        'nsfw': None,
        'resolution':0,
        'nc': None,
        'subbed': None,
        'lyrics': None,
        'uncen': None,
        'source': None,
        'overlap': None
    },
    'download': {
        'filename':'%(anime_filename)s-%(theme_slug)s.%(video_filetype)s',
        'audio_folder':None,
        'video_folder':None,
        'no_redownload':False,
        'update':False,
        'ascii':False,
        'timeout':5,
        'retries':3,
        'max_cache_age':2*24*60*60*60,
        'force_videos': []
    },
    'coverart':{
        'resolution':0,
        'folder': None,
    },
    'compression':{
        'root_dir':None,
        'base_name':'animethemes',
        'format':'tar',
        'base_dir':None
    },
    'statuses':[1,2],
    'quiet': False,
    'no_colors':False,
    'ffmpeg': 'ffmpeg',
    'ignore_prompts': False
}
OPTIONS = Options(DEFAULT)

def _update_dict(old: dict, new: dict):
    """
    Updates a dict with nested dicts.
    Skips options that do not exist.
    """
    for k,v in new.items():
        if isinstance(v, dict):
            if k in old:
                old[k] = _update_dict(old[k],v)
            else:
                logger.error(f'Cannot change option category {repr(k)}; does not exist.')
        else:
            if k in old:
                old[k] = new[k]
            else:
                logger.error(f'Cannot change value {repr(k)}.')
    
    return old

def setOptions(options: Options):
    """
    Sets `animethemes_dl.OPTIONS`.
    Look at `animethemes_dl.OPTIONS` for defaults.
    """
    global OPTIONS
    OPTIONS = Options(_update_dict(OPTIONS,options))
    
    logger.debug(f'Changed {len(options)} categories in options.')

if __name__ == "__main__":
    import json
    json.dump(
        DEFAULT,
        open('hints/settings.json','w'),
        indent=4,
        allow_nan=True
    )
    logger.info(f'Saved setting hint.')
