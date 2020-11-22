"""
Parses data and returns download data.
"""
import logging
from os import PathLike
import string
from pprint import pprint
from os.path import join, realpath, split, splitext
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from ..models.animethemes import AnimeThemeAnime, AnimeThemeEntry, AnimeThemeTheme, AnimeThemeVideo
from ..models.dldata import DownloadData
from ..options import OPTIONS
from .parser import get_animethemes
from .utils import Measure

logger = logging.getLogger('animethemes-dl')

FILENAME_BAD = set('#%&{}\\<>*?/$!\'":@+`|')
FILENAME_BANNED = set('<>:"/\\|?*')
FILENAME_ALLOWEDASCII = set(string.printable).difference(FILENAME_BANNED)

# NOTE: code could be optimized by using .pop in the for loops

def is_entry_wanted(entry: AnimeThemeEntry):
    """
    Determines wheter all the tags in the entry are the same as in OPTIONS
    """
    for k in ('spoiler','nsfw'):
        v = OPTIONS['filter']['entry'][k]
        if v is not None and entry[k] ^ v:
            return False
    return True

def is_video_wanted(video: AnimeThemeVideo):
    """
    Determines wheter all the tags in the entry are the same as in OPTIONS
    """
    for k in ('nc','subbed','lyrics','uncen'):
        v = OPTIONS['filter'][k]
        if v is not None and video[k] ^ v:
            print(k,v)
            return False
    if video['resolution'] < OPTIONS['filter']['resolution']:
        return False
    if OPTIONS['filter']['source'] is not None and video['source'] != OPTIONS['filter']['source']:
        return False
    if OPTIONS['filter']['overlap'] is not None and video['overlap'] == OPTIONS['filter']['overlap']: # uses banned instead of forced
        return False
    
    return True

def get_amount_episodes(episodes: str) -> int:
    """
    Takes in the animethemes syntax of episodes and returns it's amoutn
    """
    a = 0
    for ep in episodes.split(', '):
        if '-' in ep:
            index = ep.index('-')
            a += int(ep[:index])-int(ep[index+1:])
        else:
            a += int(ep)
    return a

def strip_illegal_chars(filename: str) -> str:
    """
    Removes all illegal chars from a filename
    """
    if OPTIONS['download']['ascii']:
        return ''.join(i for i in filename if i in FILENAME_ALLOWEDASCII)
    else:
        return ''.join(i for i in filename if i not in FILENAME_BANNED)

def generate_path(
    anime: AnimeThemeAnime, theme: AnimeThemeTheme, 
    entry: AnimeThemeEntry, video: AnimeThemeVideo) -> (
        Tuple[Optional[PathLike],Optional[PathLike]]):
    """
    Generates a path with animethemes api returns.
    Returns `(videopath|None,audiopath|None)`
    """
    formatter_attrs = (
        ('anime', anime),
        ('theme', theme),
        ('entry', entry),
        ('video', video),
        ('song', theme['song'])
    )
    formatter = {}
    for t,d in formatter_attrs:
        for k,v in d.items():
            if (not isinstance(v,(list,dict,bool)) and 
                not k.endswith('ated_at')
            ):
                formatter[t+'_'+k] = v
                
    formatter['video_filetype'] = 'webm'
    formatter['anime_filename'] = formatter['video_filename'].split('-')[0]
    
    filename = OPTIONS['download']['filename'] % formatter
    filename = strip_illegal_chars(filename)
    
    if OPTIONS['download']['video_folder']:
        video = realpath(join(OPTIONS['download']['video_folder'],filename))
    else:
        video = None
        
    if OPTIONS['download']['audio_folder']:
        audio = realpath(join(OPTIONS['download']['audio_folder'],filename))
        audio = splitext(audio)[0]+'.mp3'
    else:
        audio = None
    
    return video,audio

def pick_best_entry(theme: AnimeThemeTheme) -> (
        Optional[Tuple[AnimeThemeEntry,AnimeThemeVideo]]):
    """
    Returns the best entry and video based on OPTIONS.
    Returns None if no entry/video is wanted
    """
    # picking best entry
    entries = []
    for entry in theme['entries']:
        if not is_entry_wanted(entry):
            continue
        # picking best video
        videos = []
        for video in entry['videos']:
            if is_video_wanted(video) or video['id'] in OPTIONS['download']['force_videos']:
                videos.append(video)
        # can't append empty videos
        if videos:
            entries.append((entry,videos[0])) # pick first (best)
    
    # there's a chance no entries will be found
    if entries:
        return entries[0]
    else:
        logger.debug(f"removed {theme['song']['title']}/{theme['slug']} ({theme['id']})")
        return None

def parse_anime(anime: AnimeThemeAnime) -> Iterable[DownloadData]:
    """
    Parses an anime and yields download data.
    Returns None if invalid.
    """
    for tracknumber,theme in enumerate(anime['themes']):
        best = pick_best_entry(theme)
        if best is None:
            continue
        entry,video = best
        
        # fix some problems
        video['link'] = video['link'].replace('animethemes.dev','animethemes.moe')
        entry['version'] = entry['version'] if entry['version'] else 1
        series = [series['name'] for series in anime['series']]
        # get video path
        videopath,audiopath = generate_path(anime,theme,entry,video)
        yield {
            'url': video['link'],
            'video_path': videopath,
            'audio_path': audiopath,
            'metadata': {
                # anime
                'series': series[0] if len(series)==1 else anime['name'], # mashups are it's own thing (ie isekai quarter)
                'album': anime['name'], # discs should be numbered,
                'year': anime['year'],
                'cover': anime['cover'],
                'track': f"{tracknumber+1}/{anime['themes']}", # an ID3 "track/total" syntax
                # theme
                'title': theme['song']['title'],
                'artists': [artist['name'] for artist in theme['song']['artists']],
                'themetype': theme['slug'],
                # entry
                'version': entry['version'],
                'notes': entry['notes'],
                # video
                'resolution': video['resolution'],
                # const
                'genre': [145], # anime
                'encodedby': 'animethemes.moe',
                'cgroup': 'anime theme' # content group
            },
            'info': {
                'malid':[r['external_id'] for r in anime['resources'] if r['site']=='MyAnimeList'][0]
            }
        }
    

def filter_download_data(data: List[AnimeThemeAnime]) -> List[DownloadData]:
    """
    Sorts themes and returns List[DownloadData].
    """
    out = []
    for anime in data:
        out.extend(parse_anime(anime))
    
    return out

def get_download_data(username: str, anilist: bool = False, animelist_args={}) -> List[DownloadData]:
    """
    Gets download data from themes.moe and myanimelist.net/anilist.co.
    Returns a list of mirrors, save_paths and id3 tags.
    Sorts using `animethemes_dl.OPTIONS['options']`
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    measure = Measure()
    raw = get_animethemes(username, anilist, **animelist_args)
    data = filter_download_data(raw)
    logger.debug(f'Got {len(data)} themes from {len(raw)} anime.')
    logger.info(f'[get] Got all download data ({len(data)} entries) in {measure()}s.')
    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_download_data('sadru'))
