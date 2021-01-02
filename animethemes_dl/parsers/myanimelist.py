"""
Gets data from myanimelist.net.
"""
import logging
from datetime import datetime
from typing import List, Tuple

import requests

from ..errors import MyanimelistException
from .utils import Measure, add_url_kwargs
from ..options import OPTIONS

logger = logging.getLogger('animethemes-dl')

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
        logger.exception(f'[error] User {username} does not exist on MAL.')
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
            logger.debug(f'Got {len(data)} entries from MAL.')
            return out
        offset += 300

def parse_mal(data: list) -> List[Tuple[int,str]]:
    """
    Filters a MAL list and returns a list of malids and titles.
    Removes all unwanted statuses, scores, priorities.
    Also filters out unreleased anime.
    """
    titles = []
    for entry in data:
        status = entry['status']
        score = entry['score']
        priority = parse_priority(entry['priority_string'])
        start_date = entry['anime_start_date_string']
        malid = entry['anime_id']
        title = entry['anime_title']
        
        if not( # animelist options
            status in OPTIONS['statuses'] and
            score >= OPTIONS['animelist']['minscore'] and
            priority >= OPTIONS['animelist']['minpriority']
        ):
            continue
        
        if ( # invalid date
            start_date is None or start_date.startswith('00-00') or # didn't start
            datetime.strptime(start_date.replace('00','01'),'%d-%m-%y') > datetime.now() # didn't start yet
        ):
            continue
        
        titles.append((malid,title))
    
    return titles

def get_mal(username: str, **kwargs) -> List[Tuple[int,str]]:
    """
    Gets a MAL list with a username.
    """
    measure = Measure()
    raw = get_raw_mal(username, **kwargs)
    titles = parse_mal(raw)
    logger.info(f'[get] Got data from MAL in {measure()}s.')
    return titles

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_mal('sadru'))
