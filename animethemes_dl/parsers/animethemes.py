"""
Parses the animethemes api, getting data by title.
Uses ThreadPoolExecutor.map to get data faster on slower connections.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterable, List, Optional, Tuple

from pySmartDL.utils import get_random_useragent
from requests import Session

from ..models.animethemes import AnimeThemeAnime
from .utils import Measure

URL = "https://animethemes.dev/api/search?q={}"
MAXWORKERS = 5
session = Session()
session.headers = {
    "User-Agent":get_random_useragent()
}

logger = logging.getLogger('animethemes-dl')

def api_search(title: str) -> Dict[str,List[AnimeThemeAnime]]:
    """
    Requests a search from the api.
    """
    return session.get(URL.format(title)).json()

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

def run_executor(animelist: List[Tuple[int,str]], show_progress='') -> Iterable[AnimeThemeAnime]:
    """
    Goes thorugh anime entries and yields their api returns.
    """
    measure = Measure()
    with ThreadPoolExecutor(MAXWORKERS) as executor:
        for i,(animentry,anime) in enumerate(executor.map(request_anime,animelist),1):
            if show_progress:
                print(show_progress%(i,len(animelist)),end='\r')
            if anime:
                yield anime
    
    if show_progress: logger.info(f'[get] Got data from animethemes in {measure()}s.')

def fetch_animethemes(animelist: List[Tuple[int,str]], show_progress: str='') -> List[AnimeThemeAnime]:
    """
    Gets the anime entries from animethemes.
    Can show progress with `show_progress` string. Formats with % current,total.
    """
    return list(run_executor(animelist,show_progress))

if __name__ == "__main__":
    import json
    from .myanimelist import get_mal
    data = fetch_animethemes(get_mal('sadru'), "[^] %s/%s")
    with open('test.json','w') as file:
        json.dump(data,file,indent=4)
