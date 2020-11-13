"""
Parses data and returns download data.
"""
import logging
import string
from os.path import join,realpath,split
from .parser import get_themes
from .utils import Measure
from ..options import OPTIONS,_generate_tagsnotes

FILENAME_BAD = set('#%&{}\\<>*?/$!\'":@+`|')
FILENAME_BANNED = set('<>:"/\\|?*')
FILENAME_ALLOWEDASCII = set(string.printable).difference(FILENAME_BANNED)

def is_mirror_allowed(mirror: dict, required_tags: set=[], banned_notes: set=[]) -> bool:
    """
    Checks wheter the mirror has attributes wanted by the user.
    """
    for tag in required_tags:
        if tag not in mirror['tags']:
            return False
    
    for note in mirror['notes']:
        if note in banned_notes:
            return False
    return True

def generate_path(animelist: dict, theme: dict, mirror: dict) -> bool:
    """
    Generates a path with animelist, theme and mirror dicts
    """
    formatter = animelist.copy()
    formatter['anime_title'] = formatter.pop('title')
    formatter.update(theme);formatter.update(mirror) # I need python 3.9 so much
    formatter['short_anime_title'] = formatter.pop('short_title')
    formatter['original_filename'] = split(formatter.pop('url'))[-1]
    formatter['filetype'] = 'webm'
    del formatter['cover']
    
    filename = OPTIONS['download']['filename'] % formatter
    path = join(OPTIONS['download']['save_folder'],filename)
    return realpath(path)

def parse_theme(animelist: dict, theme: dict) -> dict:
    """
    Parses a theme and Returns download data.
    May return None if no mirror is valid.
    """
    # get the best mirror
    mirrors = theme.pop('mirrors')
    for mirror in mirrors:
        if is_mirror_allowed(mirror,*_generate_tagsnotes()):
            break
    else:
        return None
    
    return {
        'url':mirror['url'],
        'path':generate_path(animelist,theme,mirror),
        "metadata":{
            "title":theme["title"],
            "album":animelist["title"],
            "year":animelist["year"],
            "genre":145,
            "cover":animelist['cover'],
            "description":animelist['notes']
        }
    }
    

def sort_download_data(data: dict) -> list:
    """
    Sorts themes and returns a version used for animethemes-dl.
    """
    out = []
    for anime in data:
        animelist = anime.pop('animelist')
        if int(animelist['status']) in OPTIONS['statuses']:
            continue # if status is not wanted
        for theme in anime.pop('themes'):
            data = parse_theme(animelist,theme)
            if data is not None:
                out.append(data)
    
    return out
                
                

def get_download_data(username: str, anilist: bool = False, animelist_args={}) -> list:
    """
    Gets download data from themes.moe and myanimelist.net/anilist.co.
    Returns a list of mirrors, save_paths and id3 tags.
    Sorts using `animethemes_dl.OPTIONS['options']`
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    measure = Measure()
    raw = get_themes(username, anilist, **animelist_args)
    data = sort_download_data(raw)
    logging.debug(f'Filtered out {len(raw)-len(data)} entries.')
    logging.info(f'Got all download data ({len(data)} entries) in {measure()}s.')
    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_download_data('sadru'))
