"""
Parses the animethemes api, getting data by title.
Uses ThreadPoolExecutor.map to get data faster on slower connections.
"""
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from os import makedirs
from os.path import getmtime, isdir, isfile, join
from tempfile import gettempdir
from typing import Dict, Iterable, List, Optional, Tuple, Union

from pySmartDL.utils import get_random_useragent
from requests import Session

from ..errors import AnimeThemesTimeout
from ..models.animethemes import AnimeThemeAnime
from ..options import OPTIONS
from .utils import Measure

URL = "https://staging.animethemes.moe/api/search?q={}"
MAXWORKERS = 5
session = Session()
session.headers = {
    "User-Agent":get_random_useragent()
}
TEMPDIR = join(gettempdir(),'animethemes-dl')
TEMPFILE = join(TEMPDIR,'animethemes-dl-data.json')
if not isdir(TEMPDIR):
    makedirs(TEMPDIR)

logger = logging.getLogger('animethemes-dl')

def api_search(title: str) -> Union[Dict[str,List[AnimeThemeAnime]],AnimeThemesTimeout]:
    """
    Requests a search from the api.
    """
    r = session.get(URL.format(title))
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 429:
        return AnimeThemesTimeout('Got 429 from animethemes.moe.')

def make_anime_request(title: str) -> Union[List[AnimeThemeAnime],AnimeThemesTimeout]:
    """
    Requests an anime search with a title.
    Strips out unexpected characters.
    """
    title = title.split('(')[0] # remove (TV) and (<year>)
    anime = api_search(title)
    if isinstance(anime,AnimeThemesTimeout):
        return anime
    elif anime:
        return anime['anime']
    
    title = ''.join(i for i in title if not i.isdigit()) # remove numbers
    anime = api_search(title)['anime']
    if isinstance(anime,AnimeThemesTimeout):
        return anime
    elif anime:
        return anime['anime']

def get_malid(anime: AnimeThemeAnime) -> int:
    """
    Returns anime theme of resource.
    """
    for resource in anime['resources']:
        if resource["site"] == "MyAnimeList":
            return resource['external_id']

def pick_best_anime(malid: int, title: str, animes: List[AnimeThemeAnime]) -> Optional[AnimeThemeAnime]:
    """
    Goes through animes returned by api and returns the correct one.
    """
    for theme in animes:
        if malid == get_malid(theme):
            return theme
    return None

def request_anime(animentry: Tuple[int,str]) -> Tuple[Tuple[int,str],Optional[AnimeThemeAnime]]:
    """
    Makes a requests to the api with an anime entry.
    Returns anime,themes
    """
    malid,title = animentry
    anime = make_anime_request(title)
    if not isinstance(anime,AnimeThemesTimeout):
        anime = pick_best_anime(malid,title,anime)
    return animentry,anime

def run_executor(animelist: List[Tuple[int,str]], progressbar: str='') -> Iterable[AnimeThemeAnime]:
    """
    Goes thorugh anime entries and yields their api returns.
    """
    measure = Measure()
    with ThreadPoolExecutor(MAXWORKERS) as executor:
        i=0
        for i,(animentry,anime) in enumerate(executor.map(request_anime,animelist),1):
            if isinstance(anime,AnimeThemesTimeout):
                break
            if progressbar:
                print(progressbar%(i,len(animelist)),end='\r')
            if anime:
                yield anime
    
    if progressbar: logger.info(f'[get] Got {i} entries from animethemes in {measure()}s.')

def pick_needed(animelist: List[Tuple[int,str]]) -> Tuple[List[Tuple[int,str]],List[AnimeThemeAnime]]:
    """
    Takes in an animelist and returns a tuple of wanted animelist and a list of animethemes.
    """
    logger.debug(f'Loading animethemes data from {TEMPFILE}')
    animethemes = []
    animelist = {i[0]:i[1] for i in animelist}
    
    with open(TEMPFILE,'r') as file:
        for anime in json.load(file):
            malid = get_malid(anime)
            if malid in animelist:
                animethemes.append(anime)
                del animelist[malid]
    
    return list(animelist.items()),animethemes        

def fetch_animethemes(animelist: List[Tuple[int,str]]) -> List[AnimeThemeAnime]:
    """
    Gets the anime entries from animethemes or a data file younger than a day.
    Can show progress with `show_progress` string. Formats with % current,total.
    """
    progressbar = "[^] %s/%s" if logger.level<=logging.INFO else ""
    tempfile_exists = isfile(TEMPFILE) and time.time()-getmtime(TEMPFILE) <= OPTIONS['download']['max_animethemes_age']
    if tempfile_exists:
        animelist,animethemes = pick_needed(animelist)
        animethemes.extend(run_executor(animelist,progressbar))
    else:
        animethemes = list(run_executor(animelist,progressbar))
    
    with open(TEMPFILE,'w') as file:
        logger.debug(f'Storing animethemes data in {TEMPFILE}')
        json.dump(animethemes,file)
    return animethemes

if __name__ == "__main__":
    from .myanimelist import get_mal
    logger.setLevel(logging.DEBUG)
    animethemes = fetch_animethemes(get_mal('sadru'))
    with open('test.json','w') as file:
        json.dump(animethemes,file,indent=4)
