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
from typing import Dict, Iterable, List, Optional, Tuple

from pySmartDL.utils import get_random_useragent
from requests import Session

from ..models.animethemes import AnimeThemeAnime
from ..options import OPTIONS
from .utils import Measure

URL = "https://staging.animethemes.moe/api/search?q={}"
MAXWORKERS = 5
session = Session()
session.headers = {
    "User-Agent":get_random_useragent()
}
REQUEST_LOCK = True
TEMPDIR = join(gettempdir(),'animethemes-dl')
TEMPFILE = join(TEMPDIR,'animethemes-dl-data.json')
if not isdir(TEMPDIR):
    makedirs(TEMPDIR)

logger = logging.getLogger('animethemes-dl')

def _lock_requests(delay: int=30):
    """
    Locks requests because of rate limiting.
    While locked, `REQUEST_LOCK` is False.
    """
    global REQUEST_LOCK,SHOW_REQUEST_LOCK
    if REQUEST_LOCK:
        REQUEST_LOCK = False
        time.sleep(delay)
        REQUEST_LOCK = True

def api_search(title: str) -> Dict[str,List[AnimeThemeAnime]]:
    """
    Requests a search from the api.
    """
    while True:
        if REQUEST_LOCK:
            r = session.get(URL.format(title))
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                _lock_requests()

def make_anime_request(title: str) -> List[AnimeThemeAnime]:
    """
    Requests an anime search with a title.
    Strips out unexpected characters.
    """
    title = title.split('(')[0] # remove (TV) and (<year>)
    anime = api_search(title)['anime']
    if anime: return anime
    title = ''.join(i for i in title if not i.isdigit()) # remove numbers
    return api_search(title)['anime']

def pick_best_anime(malid,title, animes: List[AnimeThemeAnime]) -> Optional[AnimeThemeAnime]:
    """
    Goes through animes returned by api and returns the correct one.
    """
    for theme in animes:
        for resource in theme['resources']:
            if resource["site"] == "MyAnimeList" and resource['external_id'] == malid:
                return theme
    return None

def request_anime(animentry: Tuple[int,str]) -> Tuple[Tuple[int,str],Optional[AnimeThemeAnime]]:
    """
    Makes a requests to the api with an anime entry.
    Returns anime,themes
    """
    malid,title = animentry
    animes = make_anime_request(title)
    anime = pick_best_anime(malid,title,animes)
    return animentry,anime

def run_executor(animelist: List[Tuple[int,str]], progress: str='') -> Iterable[AnimeThemeAnime]:
    """
    Goes thorugh anime entries and yields their api returns.
    """
    measure = Measure()
    with ThreadPoolExecutor(MAXWORKERS) as executor:
        for i,(animentry,anime) in enumerate(executor.map(request_anime,animelist),1):
            if progress:
                print(progress%(i,len(animelist)),end='\r')
            if anime:
                yield anime
    
    if progress: logger.info(f'[get] Got data from animethemes in {measure()}s.')

def fetch_animethemes(animelist: List[Tuple[int,str]]) -> List[AnimeThemeAnime]:
    """
    Gets the anime entries from animethemes or a data file younger than a day.
    Can show progress with `show_progress` string. Formats with % current,total.
    """
    progress = "[^] %s/%s" if logger.level<=logging.INFO else ""
    if isfile(TEMPFILE) and time.time()-getmtime(TEMPFILE) <= OPTIONS['download']['max_animethemes_age']:
        logger.info(f'[get] Loaded previous data from animethemes.')
        with open(TEMPFILE,'r') as file:
            return json.load(file)
    else:
        data = list(run_executor(animelist,progress))
        with open(TEMPFILE,'w') as file:
            logger.debug(f'Storing animethemes data in {TEMPFILE}')
            json.dump(data,file)
        return data

if __name__ == "__main__":
    from .myanimelist import get_mal
    logger.setLevel(logging.DEBUG)
    data = fetch_animethemes(get_mal('sadru'))
    with open('test.json','w') as file:
        json.dump(data,file,indent=4)
