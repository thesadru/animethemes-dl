"""
Gets data from anilist.co.
"""
import logging
from datetime import datetime
from typing import List, Tuple

import requests

from ..errors import AnilistException
from .utils import Measure
from ..options import OPTIONS

logger = logging.getLogger('animethemes-dl')

ALURL = 'https://graphql.anilist.co'
ALQUERY = """
query userList($user: String) {
  MediaListCollection(userName: $user, type: ANIME) {
    lists {
      status
      entries {
        status
        score
        priority
        media {
          idMal
          title {
            romaji
          }
          startDate {
            year
            month
            day
          }
        }
      }
    }
  }
}
"""

def get_raw_anilist(username: str, query: str=ALQUERY, **vars) -> dict:
    """
    Gets an anilist list with a username.
    Takes an optional query and variables.
    `vars['user']` will be set to `username`.
    """
    vars['user'] = username
    json_arg = {'query': query, 'variables': vars}
    
    r = requests.post(ALURL,json=json_arg)
    if r.status_code == 200:
        data = r.json()
    else:
        return r.raise_for_status()
    
    if "errors" in data:
        errors = '; '.join(i['message'] for i in data['errors'])
        logger.exception(f'[error] {errors}')
        raise AnilistException(errors)
    else:
        lists = data['data']["MediaListCollection"]["lists"]
        logger.debug(f'Got {sum(len(i) for i in lists)} enries from anilist.')
        return lists

def sort_anilist(data: dict) -> List[Tuple[int,str]]:
    """
    Filters an anilist list and returns a list of titles.
    Removes all unwanted statuses, scores, priorities.
    Also filters out unreleased anime.
    """
    titles = []
    for i in data:
        status = {
            'CURRENT':1,
            'COMPLETED':2,
            'PAUSED':3,
            'DROPPED':4,
            'PLANNING':6,
            'REPEATING':1, # rewatching
        }[i['status']]
        for entry in i['entries']:
            media = entry.pop('media')
            score = entry['score']
            priority = entry['priority']
            start_date = media['startDate']
            malid = media['idMal']
            title = media['title']['romaji']
            
            if not( # animelist options
                status in OPTIONS['statuses'] and
                score >= OPTIONS['animelist']['minscore'] and
                priority >= OPTIONS['animelist']['minpriority']
            ):
                continue
            
            if ( # invalid date
                None in start_date['year'].values() or # didn't start
                datetime(**start_date) > datetime.now() # didn't start yet
            ):
                continue
            titles.append((malid,title))
    
    return titles

def get_anilist(username: str, **vars) -> List[Tuple[int,str]]:
    """
    Gets an anilist list with a username.
    """
    measure = Measure()
    raw = get_raw_anilist(username, **vars)
    data = sort_anilist(raw)
    logger.info(f'[get] Got data from anilist in {measure()}s.')
    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_anilist('sadru'))
