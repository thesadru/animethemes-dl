"""
pulls from animethemes and MAL/AniList
sort and modify the gotten list
"""
import requests
import json
import sys
import time
from printer import fprint
from globals import Opts

THEMESURL = 'https://animethemes-api.herokuapp.com/api/v1/'
MALURL = 'https://myanimelist.net/animelist/{user}/load.json'
ALURL = 'https://graphql.anilist.co'
ALQUERY = """
query userList($user: String) {
    MediaListCollection(userName: $user, type: ANIME) {
        lists {
            entries {
                status
                score
                priority
                media {
                    idMal
                    title {
                        romaji
                    }
                }
            }
        }
    }
}
"""

def themes_get(*args,**kwargs):
    """
    get data from animethemes-api
    args reffer to the url ('id',12345) -> URL/id/12345
    kwargs reffer to the arguments (sort=3,x='w') -> ?sort=3&x=w
    """
    url = THEMESURL+'/'.join(map(str,args))
    url += '&'.join(k+'='+str(v) for k,v in kwargs.items())
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def get_mirror_value(mirror):
    """
    get a value of the mirror with Opts.Download.preffered
    adds extra points based on the amount of tags (0.1 for every tag)
    """
    mirror = mirror['quality'].lower()
      
    value = 0
    points = len(Opts.Download.preffered)
    for i in Opts.Download.preffered:
        if i in mirror:
            value += points
        points -= 1
    if len(mirror) > 0:
        value += 0.1*(mirror.count(',')+1)
    return value

def parse_anime(anime):
    """
    parses anime data
    adds short_title and sorts mirrors
    """
    new_themes = {}
    for theme in anime['themes']:
        
        type_short = theme['type'].split()
        if len(type_short) == 2:
            type_short,type_long = type_short
        else:
            type_short = type_short[0]
        
        if type_short in new_themes:
            new_themes[type_short]['mirrors'].extend(theme['mirrors'])
        else:
            theme['type'] = type_short
            new_themes[type_short] = theme
    
    anime["short_title"] = (theme["mirrors"][0]["mirror"][30:].split('-')[0])
    new_themes_parsed = []
    for theme in new_themes.values():
        theme['mirrors'].sort(key=get_mirror_value,reverse=True)
        new_themes_parsed.append(theme)
    anime['themes'] = new_themes_parsed
    
    return anime

def get_themes(username,type='mal'):
    """
    gets parsed themes with a username and type ['mal' | 'anilist]
    """
    if username == '':
        return []
    Opts.Download.preffered = [i.lower() for i in Opts.Download.preffered]
    
    data = themes_get(type,username)
    for i,anime in enumerate(data):
        data[i] = parse_anime(anime)

    return data

def mal_get_short(username,**kwargs):
    """
    gets a MAL list with a username
    kwargs reffer to the arguments (sort=3,x='w') -> ?sort=3&x=w
    """
    url = MALURL.format(user=username)+'?'
    url += '&'.join(k+'='+str(v) for k,v in kwargs.items())
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        if r.status_code == 500:
            fprint('error','too many requests made, try again later')
        r.raise_for_status()
        

def mal_get_unsorted(username,**kwargs):
    """
    gets your entire list if it goes over 300 anime
    """
    out = []
    offset = 0
    while True:
        kwargs['offset'] = offset
        data = mal_get_short(username,**kwargs)
        if data:
            out.extend(data)
        elif len(data) < 300: # no more anime
            return out
        offset += 300

def mal_get(username,**kwargs):
    """
    gets your entire list sorted by status
    """
    if username == '':
        return []
    out = [[] for _ in range(0,7)]
    data = mal_get_unsorted(username,**kwargs)
    for anime in data:
        out[anime['status']].append(anime)
    
    return out

def sort_al(data):
    """
    sorts out AniList data by status to resemble MAL's system
    """
    out = [[] for _ in range(0,7)]
    data = data["data"]["MediaListCollection"]["lists"]
    for entries in data:
        entries = entries['entries']
        status = {
            'PLANNING':6,
            'CURRENT':1,
            'COMPLETED':2,
            'DROPPED':4,
            'PAUSED':3
        }[entries[0]['status']]
        for entry in entries:
            out[status].append({
                'status':status,
                'score':entry['score'],
                'priority_string':entry['priority'],
                'anime_id':entry['media']['idMal'],
                'anime_title':entry['media']['title']['romaji']
            })
    return out

def al_get(username,variables={}):
    """
    gets data from AniList using 
    variables reffer to JQuery variables
    """
    if username == '':
        return []
    variables['user'] = username
    json_arg = {'query': ALQUERY, 'variables': variables}
    r = requests.post(ALURL,json=json_arg)
    if "errors" in r:
        fprint('error',f"{'; '.join(i['message'] for i in r['errors'])}\n{r['errors']}")
    if r.status_code == 200:
        return sort_al(r.json())
    else:
        r.raise_for_status()
    

def get_proper(username,anilist=False,extra_ids=[],**mal_kwargs):
    """
    gets proper data from MAL/AniList
    sorted by status (0 = extra ids)
    """
    t = time.time()
    fprint('get',f'getting data from {"anilist.co" if anilist else "myanimelist.net"}',end='')
    if anilist:
        list_data = al_get(username)
    else:
        list_data = mal_get(username,**mal_kwargs)
    fprint(' | '+str(int((time.time()-t)*1000))+'ms')
    
    t = time.time()
    fprint('get','getting data from themes.moe',end='')
    if anilist:
        themes_data = get_themes(username,'anilist')
    else:
        themes_data = get_themes(username,'mal')
    extra_themes_data = []
    for malid in extra_ids:
        data = parse_anime(themes_get('id',malid))
        data['mal_data'] = {
            'status':5,
            'score':10,
            'priority_string':'High',
            'anime_id':malid,
            'anime_title':''
        }
        extra_themes_data.append(data)
    fprint(' | '+str(int((time.time()-t)*1000))+'ms')
    
    
    mal_dict = {} # {12345:{'mal_data':{...},'status':1},...}
    for status,animes in enumerate(list_data):
        for anime in animes:
            mal_dict[anime['anime_id']] = {'mal_data':anime,'status':status}

    mal_list = {i:[] for i in range(0,7)}
    for anime in themes_data:
        mal_id = anime['mal_id']
        if mal_id not in mal_dict:
            continue
        status = mal_dict[mal_id]['status']
        mal_data = mal_dict[mal_id]['mal_data']
        anime['mal_data'] = mal_data
        mal_list[status].append(anime)
        
    mal_list[0] = extra_themes_data
    
    return mal_list
    
if __name__ == '__main__':
    Opts.Print.quiet = False
    Opts.Download.preffered = []
    
    x = get_proper('sadru',False)
    y = get_proper('sadru',True)
    json.dump(x,open('animethemes.malsave.json','w'),indent=4)
    json.dump(y,open('animethemes.alsave.json','w'),indent=4)
    
    # x = mal_get('sadru')
    # y = al_get('sadru')
    # json.dump(x,open('animethemes.malsave.json','w'),indent=4)
    # json.dump(y,open('animethemes.alsave.json','w'),indent=4)