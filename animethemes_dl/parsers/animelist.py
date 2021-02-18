"""
File for fetching and parsing data of animelists.
Made to be extendible with classes.
"""
from animethemes_dl.models.animelist import AnimeListEntry
import json
import logging
from datetime import datetime
from itertools import count
from typing import Any, List

import requests

from ..errors import AnimeListException
from ..models import AnimeListDict, AnimeListSite
from ..options import OPTIONS
from ..tools import cache_is_young_enough, get_tempfile_path
from .utils import Measure, add_url_kwargs

logger = logging.getLogger('animethemes-dl')

class AnimeListBase:
    name: str
    url: str
    def __init__(self, **kwargs):
        """Initializes AnimeList fetcher, can take extra settings"""
        assert self.name in ANIMELISTSITES
        self.kwargs = kwargs
    
    def fetch_raw(self, username: str) -> Any:
        """Fetches raw data from the animelist."""
        ...
    def parse(self, raw: Any) -> List[AnimeListDict]:
        """Parses raw data, returns normalized one."""
        ...
    
    def filter(self, data: List[AnimeListDict]) -> List[AnimeListEntry]:
        """
        Filters parsed data, looks at status, score, priority and start date.
        """
        date_now = datetime.now()
        titles = []
        for entry in data:
            if (
                entry['status'] in OPTIONS['statuses'] and
                entry['score'] >= OPTIONS['animelist']['minscore'] and
                entry['priority'] >= OPTIONS['animelist']['minpriority'] and
                entry['start_date'] is not None and entry['start_date'] <= date_now
            ): 
                titles.append((entry['title'],entry['malid'],self.name))
            
        return titles
    
    def get_titles(self, username: str) -> List[AnimeListEntry]:
        """
        Gets titles by fetching or loading raw data, then parsing it.
        """
        CACHEFILE = get_tempfile_path(self.name.lower()+'.json')
        measure = Measure()
        
        if cache_is_young_enough(CACHEFILE):
            with open(CACHEFILE) as file:
                logger.debug(f'Loading {self.name} data from {CACHEFILE}')
                raw = json.load(file)
        else:
            raw = self.fetch_raw(username)
        
        with open(CACHEFILE,'w') as file:
            logger.debug(f'Storing {self.name} data in {CACHEFILE}')
            json.dump(raw,file)
        
        data = self.parse(raw)
        titles = self.filter(data)
        
        logger.info(f'[get] Got data from {self.name} in {measure()}s.')
        if any(OPTIONS['animelist']['range']):
            s,e = OPTIONS['animelist']['range']
            return titles[s:e]
        else:
            return titles

# =============================================================================

class MyAnimeList(AnimeListBase):
    name = "MyAnimeList"
    url = "https://myanimelist.net/animelist/{}/load.json"
    
    def fetch_raw(self, username: str) -> List[dict]:
        kwargs = self.kwargs.copy()
        baseurl = self.url.format(username)
        out = []
        
        for offset in count(0,300):
            kwargs['offset'] = offset
            url = add_url_kwargs(baseurl,self.kwargs)
            
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
            else:
                raise AnimeListException(f'User {username} does not exist on {self.name}.')
            
            out.extend(data)
            if len(data) < 300: # no more anime
                return out
    
    def parse(self, raw: List[dict]) -> List[AnimeListDict]:
        data = []
        for entry in raw:
            data.append({
                'title': entry['anime_title'],
                'malid': entry['anime_id'],
                'status': entry['status'],
                'score': entry['score'],
                'priority': ('low','medium','high').index(entry['priority_string'].lower()),
                'start_date': None if entry['anime_start_date_string'] is None or '00' in entry['anime_start_date_string'] else 
                    datetime.strptime(entry['anime_start_date_string'].replace('00','01'),r'%d-%m-%y')
            })
        
        return data


class AniList(AnimeListBase):
    name = "AniList"
    url = "https://graphql.anilist.co"
    query = """
query userList($user: String) {
  MediaListCollection(userName: $user, type: ANIME) {
    lists {
      status
      entries {
        status
        score
        priority
        media {
          id
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
    """.strip()
    
    def fetch_raw(self, username: str) -> List[dict]:
        kwargs = self.kwargs.copy()
        kwargs['user'] = username
        json_arg = {'query': self.query, 'variables': kwargs}
        
        r = requests.post(self.url, json=json_arg)
        r.raise_for_status()
        
        data = r.json()
        
        if "errors" in data:
            errors = '; '.join(i['message'] for i in data['errors'])
            raise AnimeListException(errors)
        else:
            lists = data['data']["MediaListCollection"]["lists"]
            return lists
    
    def parse(self, data: List[dict]) -> List[AnimeListDict]:
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
                titles.append({
                    'title': entry['media']['title']['romaji'],
                    'malid': entry['media']['id'],
                    'status': status,
                    'score': entry['score'],
                    'priority': entry['priority'],
                    'start_date': None if None in entry['media']['startDate'].values() else 
                        datetime(**entry['media']['startDate'])
                })
        
        return titles


ANIMELISTSITES = {"AniList":AniList, "MyAnimeList": MyAnimeList}