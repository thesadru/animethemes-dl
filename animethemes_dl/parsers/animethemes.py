"""
Parses the animethemes api, getting data by title.

- load data from cache
  - animethemes,unavalible = load_cache()
    - animethemes: list[AnimeThemeAnime]
    - unavalible: dict[site_name:set[site_id]]
  - animelist = get_old()
    - sorted by _fetched_at
- organize animethemes into dict by id
- start fetching data
  - every time a request is fetched, update animethemes with it
  - if the request is invalid, add it to unavalible
- save data to cache
- return animethemes
"""
from animethemes_dl.models.animelist import AnimeListSite
import json
import logging
from os.path import isfile
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterable, List, Optional, Set, Tuple

from pySmartDL.utils import get_random_useragent
from requests import Session

from ..errors import AnimeThemesTimeout
from ..models import AnimeThemeAnime
from ..options import OPTIONS
from .utils import Measure, remove_bracket, simplify_title, add_honorific_dashes
from ..tools import get_tempfile_path, cache_is_young_enough

URL = "https://staging.animethemes.moe/api/search?q={}"
MAXWORKERS = 5
session = Session()
session.headers = {
    "User-Agent":get_random_useragent()
}
session.requests_remaining = float('inf')
CACHEFILE = get_tempfile_path('animethemes.json')

logger = logging.getLogger('animethemes-dl')


def api_search(title: str) -> Dict[str,List[AnimeThemeAnime]]:
    """
    Requests a search from the api.
    """
    if session.requests_remaining < 5:
        return None
    r = session.get(URL.format(title))
    session.requests_remaining = min(session.requests_remaining, int(r.headers.get('X-RateLimit-Remaining',0)))
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 429:
        raise AnimeThemesTimeout('Got 429 error from animethemes.moe, please wait 30s to get the rest of entries.')
    else:
        r.raise_for_status()

def verify_anime(animes: List[AnimeThemeAnime], alid: int, alsite: AnimeListSite) -> Optional[AnimeThemeAnime]:
    """
    Takes in a list of anime and figures out the correct one.
    Returns None if no anime is right
    alid is the external id in list site and alsite is the name of the anime list site.
    """
    for anime in animes:
        for resource in anime['resources']:
            if resource['site']==alsite and resource['external_id']==alid:
                return anime
    return None

def fetch_anime(title: str, alid: int, alsite: AnimeListSite) -> Optional[AnimeThemeAnime]:
    """
    Requests an anime search with a title.
    alid is the external id in list site and alsite is the name of the anime list site.
    Can modify the title and send a request up to 3 times, before finding the right data.
    """
    for func in (remove_bracket,simplify_title,add_honorific_dashes):
        title = func(title)
        data = api_search(title)
        if data is None: return None
        anime = verify_anime(data['anime'],alid,alsite)
        if anime is not None: return anime
    
    return None

def load_cache(animelist: List[Tuple[str,int,AnimeListSite]]) -> (
        Tuple[List[Tuple[str,int,AnimeListSite]], Dict[int,AnimeThemeAnime], Dict[Tuple[AnimeListSite,int],Tuple[str,int]]]):
    """
    Loads cache and figures out which entries need to be updated.
    """
    current_time = time.time()
    logger.debug(f'Loading animethemes data from {CACHEFILE}')
    animelist = {(site,alid):title for title,alid,site in animelist}
    
    with open(CACHEFILE) as file:
        data = json.load(file)
        animethemes: list[AnimeThemeAnime] = sorted(data['anime'], key=lambda x:x['_fetched_at'])
        unavalible: dict[tuple[AnimeListSite,int],tuple[str,int]] = {(i['site'],i['alid']):(i['title'],i['fetched_at']) for i in data['unavalible_anime']}

    for anime in animethemes:
        for resource in anime['resources']:
            if (resource['site'],resource['external_id']) in animelist and current_time-anime['_fetched_at'] <= OPTIONS['download']['max_cache_age']:
                del animelist[resource['site'],resource['external_id']]
    
    for (site,alid),(title,fetched_at) in unavalible.items():
        if (site,alid) in animelist and current_time-fetched_at <= OPTIONS['download']['max_cache_age']:
            del animelist[site,alid]
    
    animelist = [(title,alid,site) for (site,alid),title in animelist.items()]
    animethemes = {anime['id']:anime for anime in animethemes}
    
    return animelist,animethemes,unavalible

def save_cache(animethemes: List[AnimeThemeAnime], unavalible: Dict[Tuple[AnimeListSite,int],Tuple[str,int]]):
    """
    Saves data to cache.
    """
    logger.debug('Saving animethemes data at {CACHEFILE}')
    unavalible = [{'title':title,'alid':alid,'site':site,'fetched_at':fetched_at} for (site,alid),(title,fetched_at) in unavalible.items()]
    with open(CACHEFILE,'w') as file:
        json.dump({
            'anime':animethemes,
            'unavalible_anime':unavalible
        },file)

def fetch_animethemes(animelist: List[Tuple[str,int,AnimeListSite]], use_cache=True) -> List[AnimeThemeAnime]:
    m = Measure()
    
    if use_cache and isfile(CACHEFILE):
        animelist,animethemes,unavalible = load_cache(animelist)
    else:
        animethemes,unavalible = {},{}
    fetched,failed,total = 0,0,len(animelist)
    
    if animelist:
        with ThreadPoolExecutor(MAXWORKERS) as executor:
            futures = [(executor.submit(fetch_anime, *al),al) for al in reversed(animelist)]
            
            try:
                while futures:
                    anime,al = futures.pop()
                    anime = anime.result()
                    if anime is not None:
                        anime['_fetched_at'] = time.time()
                        animethemes[anime['id']] = anime
                        fetched += 1
                    else:
                        unavalible[al[2],al[1]] = (al[0],time.time())
                        failed += 1
                if logger.level <= logging.INFO:
                    print(f"\r^ {fetched+failed}/{total}",end='',flush=True)
            
            except AnimeThemesTimeout as e:
                logger.error(f'[error] {e.args[0]}')
                print(futures)
            finally:
                for future in futures: future[0].cancel()
    
    animethemes = list(animethemes.values())
    if use_cache and animelist:
        save_cache(animethemes,unavalible)
    
    if animelist:
        if logger.level <= logging.INFO: print()
        logger.info(f"[get] Got {fetched+failed}/{total} entries{(f' ({failed} unavalible) ' if failed else ' ')}from animethemes.moe")
    else:
        logger.info(f'[get] Loaded {len(animethemes)} cached entries from animethemes.moe')
    
    return animethemes
