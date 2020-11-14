"""
Gets data from myanimelist.net.
"""
import logging

import requests

from ..errors import MyanimelistException
from ..models import RawAnimeList
from .utils import Measure, add_url_kwargs

MALURL = 'https://myanimelist.net/animelist/{user}/load.json'

def parse_priority(priority: str) -> int:
    """
    Parses MAL priority string into a 1-3 range
    """
    return ('low','medium','high').index(priority.lower())

def get_mal_part(username: str, **kwargs) -> list:
    """
    Gets a MAL list with a username.
    Kwargs reffer to the arguments `(sort=3,x='w') -> ?sort=3&x=w`.
    If a list is longer than 300 entries, you must set an offset.
    """
    url = MALURL.format(user=username)
    url = add_url_kwargs(url,kwargs)
    
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        logging.exception(f'User {username} does not exist on MAL.')
        raise MyanimelistException(f'User {username} does not exist on MAL.')

def get_raw_mal(username: str, **kwargs) -> list:
    """
    Gets a MAL list with a username.
    Sends multiple requests if the list is longer than 300 entries.
    """
    out = []
    offset = 0
    while True:
        kwargs['offset'] = offset
        data = get_mal_part(username, **kwargs)
        out.extend(data)
        if len(data) < 300: # no more anime
            logging.debug(f'Got {len(data)} entries from MAL.')
            return out
        offset += 300

def sort_mal(data: list) -> RawAnimeList:
    """
    Sorts a MAL list and returns a version used for animethemes-dl.
    """
    out = []
    for entry in data:
        priority = parse_priority(entry['priority_string'])
        out.append({
            'status':entry['status'],
            'score':entry['score'],
            'priority':priority,
            'notes':entry['tags'],
            'malid':entry['anime_id'],
            'title':entry['anime_title'],
            'cover':entry['anime_image_path'], #inclusing the access token
            'episodes':entry['anime_num_episodes']
        })
    
    return out

def get_mal(username: str, **kwargs) -> RawAnimeList:
    """
    Gets a MAL list with a username.
    """
    measure = Measure()
    raw = get_raw_mal(username, **kwargs)
    data = sort_mal(raw)
    logging.info(f'Got data from MAL in {measure()}s.')
    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_mal('sadru'))
