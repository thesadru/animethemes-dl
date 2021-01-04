"""
Parses the animethemes api, getting data by title.
Uses ThreadPoolExecutor.map to get data faster on slower connections.
"""
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterable, List, Optional, Tuple

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
CACHEFILE = get_tempfile_path('animethemes.json')

logger = logging.getLogger('animethemes-dl')

def api_search(title: str) -> Dict[str,List[AnimeThemeAnime]]:
    """
    Requests a search from the api.
    """
    r = session.get(URL.format(title))
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 429:
        raise AnimeThemesTimeout('Got 429 error from animethemes.moe, please wait 30s to get the rest of entries.')
    else:
        r.raise_for_status()

def make_anime_request(title: str) -> List[AnimeThemeAnime]:
    """
    Requests an anime search with a title.
    Strips out unexpected characters.
    """
    for func in (remove_bracket,simplify_title,add_honorific_dashes):
        title = func(title)
        anime = api_search(title)['anime']
        if anime:
            return anime
    
    return []

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
    for anime in animes:
        if malid == get_malid(anime):
            return anime
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

def run_executor(animelist: List[Tuple[int,str]], progressbar: str='') -> Iterable[AnimeThemeAnime]:
    """
    Goes thorugh anime entries and yields their api returns.
    """
    measure = Measure()
    total_fetched = 0
    total_failed = 0
    total_expected = len(animelist)
    
    with ThreadPoolExecutor(MAXWORKERS) as executor:
        try:
            for animentry,anime in executor.map(request_anime,animelist):
                if anime:
                    total_fetched += 1
                else:
                    total_failed += 1
                    anime = {
                        'created_at':None,'updated_at':None, # invalid created at means that there's no entry in the API
                        'title':animentry[1],
                        'resources':[{'site':'MyAnimeList','external_id':animentry[0]}]
                    } 
                
                anime['_fetched_at'] = time.time()
                yield anime
                
                if progressbar:
                    print(progressbar%(total_fetched+total_failed,total_expected),end='\r')
                
        except AnimeThemesTimeout as e:
            logger.error(e.args[0])
        except Exception as e:
            logger.exception(e)
    
    if progressbar: logger.info(
        f'[get] Got {total_fetched}/{total_expected}' + 
        f'{f" ({total_failed} unavalible) " if total_failed else " "}' + 
        f'entries from animethemes in {measure()}s.')

def pick_needed(animelist: List[Tuple[int,str]]) -> Tuple[List[Tuple[int,str]],List[AnimeThemeAnime]]:
    """
    Takes in an animelist and returns a tuple of wanted animelist and a list of animethemes.
    """
    logger.debug(f'Loading animethemes data from {CACHEFILE}')
    animethemes = []
    animelist = dict(animelist)
    
    with open(CACHEFILE) as file:
        for anime in json.load(file):
            malid = get_malid(anime)
            if malid in animelist and time.time()-anime['_fetched_at'] <= OPTIONS['download']['max_cache_age']:
                animethemes.append(anime)
                del animelist[malid]
    
    return list(animelist.items()),animethemes        

def fetch_animethemes(animelist: List[Tuple[int,str]]) -> List[AnimeThemeAnime]:
    """
    Gets the anime entries from animethemes or a data file younger than a day.
    Can show progress with `show_progress` string. Formats with % current,total.
    """
    progressbar = "[^] %s/%s" if logger.level<=logging.INFO else ""
    if cache_is_young_enough(CACHEFILE):
        animelist,animethemes = pick_needed(animelist)
        if animelist:
            animethemes.extend(run_executor(animelist,progressbar))
    else:
        animethemes = list(run_executor(animelist,progressbar))
    
    with open(CACHEFILE,'w') as file:
        logger.debug(f'Storing animethemes data in {CACHEFILE}')
        json.dump(animethemes,file)
    
    return [anime for anime in animethemes if anime['created_at'] is not None] # remove unexisting api entries

if __name__ == "__main__":
    from .animelist import MyAnimeList
    logger.setLevel(logging.DEBUG)
    animethemes = fetch_animethemes(MyAnimeList().get_titles('sadru'))
    with open('test.json','w') as file:
        json.dump(animethemes,file,indent=4)
