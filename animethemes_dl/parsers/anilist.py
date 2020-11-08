"""
Gets data from anilist.co.
"""
import requests

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
        raise Exception('; '.join(i['message'] for i in data['errors']))
    else:
        return data['data']

def sort_anilist(data: dict) -> dict:
    """
    Sorts an anilist list and returns a version used for animethemes-dl.
    """
    out = {i:[] for i in range(1,7)}
    data = data["MediaListCollection"]["lists"]
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
            out[status].append({
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

def get_anilist(username: str, **vars) -> dict:
    raw = get_raw_anilist(username,vars=vars)
    return sort_anilist(raw)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_anilist('sadru'))
