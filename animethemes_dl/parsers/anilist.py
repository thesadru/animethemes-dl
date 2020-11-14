"""
Gets data from anilist.co.
"""
import logging

import requests

from ..errors import AnilistException
from ..models import RawAnimeList
from .utils import Measure

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
        repeat
        notes
        media {
          idMal
          title {
            romaji
          }
          episodes
          coverImage {
            medium
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

def sort_anilist(data: dict) -> RawAnimeList:
    """
    Sorts an anilist list and returns a version used for animethemes-dl.
    """
    out = []
    for i in data:
        status = i['status']
        status = {
            'CURRENT':1,
            'COMPLETED':2,
            'PAUSED':3,
            'DROPPED':4,
            'PLANNING':6,
            'REPEATING':1, # rewatching
        }[status]
        entries = i['entries']
        for entry in entries:
            media = entry.pop('media')
            out.append({
                'status':status,
                'score':entry['score'],
                'priority':entry['priority'],
                'notes':entry['notes'] or '',
                'malid':media['idMal'],
                'title':media['title']['romaji'],
                'cover':media['coverImage']['medium'],
                'episodes':media['episodes']
            })
    
    return out

def get_anilist(username: str, **vars) -> RawAnimeList:
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