"""
Gets data from themes.moe using their API.
"""
import logging

import requests

from ..models import RawAnimeThemes
from .utils import Measure

logger = logging.getLogger(__name__)

THEMESMALURL = 'https://themes.moe/api/mal/{user}'
THEMESALURL  = 'https://themes.moe/api/al/{user}'
POSSIBLETAGS = [
    'NC',
    'Subbed',
    'Lyrics',
    'Cen',
    'Uncen',
    '60FPS',
    'Trans',
    'BD',
    '420',
    '720',
    '1080'
]
POSSIBLENOTES = [
    'Spoiler',
    'NSFW'
]

def get_tags(s: str, possible: list=POSSIBLETAGS) -> list:
    """
    Gets tags from a url
    """
    tags = []
    for tag in possible:
        if tag in s:
            tags.append(tag)
    return tags

def parse_theme_type(themetype: str) -> tuple:
    """
    Parser a themetype into a `(type, short type, version)` tuple.
    """
    themetype = themetype.split()
    if len(themetype) == 1:
        themetype = themetype[0]
        version = 1
    else:
        themetype,version = themetype
        version = int(version[1:])
    
    shortype = themetype[:2]
    return themetype,shortype,version
    

def get_raw_animethemes(username: str, anilist: bool = False) -> list:
    """
    Gets themes from r/animethemes using the themes.moe api.
    """
    if anilist:
        url = THEMESALURL.format(user=username)
    else:
        url = THEMESMALURL.format(user=username)
    
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        logger.debug(f'Got {len(data)} entries from themes.moe.')
        return data
    else:
        r.raise_for_status()

def sort_animethemes(data: list) -> RawAnimeThemes:
    """
    Sorts themes and returns a version used for animethemes-dl.
    """
    out = []
    url = ''
    
    for entry in data:
        themes = {}
        for theme in entry['themes']:
            themetype,shortype,version = parse_theme_type(theme['themeType'])
            mirror = theme['mirror']
            url = mirror['mirrorURL']
            tags = get_tags(url)
            notes = get_tags(mirror['notes'],POSSIBLENOTES)
            
            if themetype not in themes:
                themes[themetype] = {
                    'title':theme['themeName'],
                    'type': themetype,
                    'shortype':shortype,
                    'mirrors':[]
                }
            
            themes[themetype]['mirrors'].append({
                'url': url,
                'version':version,
                'tags': tags,
                'notes': notes,
                'priority': mirror['priority'],
            })
        sorted_themes = []
        for theme in themes.values():
            theme['mirrors'].sort(key=lambda mirror: mirror['priority'])
            sorted_themes.append(theme)
        
        short_title = url.split('/')[-1].split('-')[0]
        
        out.append({
            'themes': sorted_themes,
            'animelist':{
                'malid':entry['malID'],
                'status':entry['watchStatus'],
                'short_title':short_title,
                'year':entry['year'],
                'season': entry['season'],
            }
        })
    
    return out

def get_animethemes(username: str, anilist: bool = False) -> RawAnimeThemes:
    """
    Gets themes with a username.
    """
    measure = Measure()
    raw = get_raw_animethemes(username, anilist)
    data = sort_animethemes(raw)
    logger.info(f'Got data from themes.moe in {measure()}s.')
    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_animethemes('sadru'))
