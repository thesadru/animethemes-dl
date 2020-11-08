"""
Gets data from myanimelist.net.
"""
from .utils import add_url_kwargs
import requests

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
        r.raise_for_status()

def get_raw_mal(username: str, **kwargs) -> list:
    """
    Gets a MAL list with a username.
    Sends multiple requests if the list is longer than 300 entries.
    """
    out = []
    offset = 0
    while True:
        kwargs['offset'] = offset
        data = get_mal_part(username,kwargs=kwargs)
        out.extend(data)
        if len(data) < 300: # no more anime
            return out
        offset += 300

def sort_mal(data: list) -> dict:
    """
    Sorts a MAL list and returns a version used for animethemes-dl.
    """
    out = {i:[] for i in range(1,7)}
    for entry in data:
        status = entry['status']
        priority = parse_priority(entry['priority_string'])
        out[status].append({
            'status':status,
            'score':entry['score'],
            'priority':priority,
            'notes':entry['tags'],
            'malid':entry['anime_id'],
            'title':entry['anime_title'],
            'cover':entry['anime_image_path'],
            'episodes':entry['anime_num_episodes']
        })
    
    return out

def get_mal(username: str, **kwargs) -> dict:
    """
    Gets a MAL list with a username.
    """
    raw = get_raw_mal(username, kwargs=kwargs)
    return sort_mal(raw)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_mal('sadru'))
