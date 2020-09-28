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

class MirrorSorter:
    def __init__(self, obj, *args):
        self.obj = obj
    def __lt__(self, other):
        return self.cmp(self.obj, other.obj) < 0
    def __gt__(self, other):
        return self.cmp(self.obj, other.obj) > 0
    def __eq__(self, other):
        return self.cmp(self.obj, other.obj) == 0
    def __le__(self, other):
        return self.cmp(self.obj, other.obj) <= 0  
    def __ge__(self, other):
        return self.cmp(self.obj, other.obj) >= 0
    def __ne__(self, other):
        return self.cmp(self.obj, other.obj) != 0
    @staticmethod
    def cmp(x,y):
        # swap them because sort works weirdly
        x,y = y['quality'],x['quality']
        
        # total points
        n = 0
        # points start from highest to lowest
        p = len(Opts.Download.preffered)
        for i in Opts.Download.preffered:
            if i in x:
                n += p
            if i in y:
                n -= 1
            p -= 1
        # if they are the same, simply return the one with more tags
        if n == 0:
            return x.count(',')+(len(x)>0) - y.count(',')+(len(y)>0)
        return n


def themes_get(*args):
    url = THEMESURL+'/'.join(map(str,args))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def get_themes(username,type='mal'):
    data = themes_get(type,username)
    for i,anime in enumerate(data):
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
                
        data[i]["short_title"] = (theme["mirrors"][0]["mirror"][30:].split('-')[0])
        for theme in new_themes.values():
            theme['mirrors'].sort(key=MirrorSorter)
            data[i]['themes'].append(theme)
            
    return data

def mal_get_short(username,**kwargs):
    url = MALURL.format(user=username)+'?'
    url = url + '&'.join(k+'='+str(v) for k,v in kwargs.items())
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()
        

def mal_get_unsorted(username,**kwargs):
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
    out = [[] for _ in range(0,7)]
    data = mal_get_unsorted(username,**kwargs)
    for anime in data:
        out[anime['status']].append(anime)
    
    return out

def sort_al(data):
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
    variables['user'] = username
    json_arg = {'query': ALQUERY, 'variables': variables}
    r = requests.post(ALURL,json=json_arg)
    if "errors" in r:
        fprint('error',f"{'; '.join(i['message'] for i in r['errors'])}\n{r['errors']}")
    if r.status_code == 200:
        return sort_al(r.json())
    else:
        r.raise_for_status()
    

def get_proper(username,anilist=False,**mal_kwargs):
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
    fprint(' | '+str(int((time.time()-t)*1000))+'ms')
    
    fprint('parse','sorting data for later use')
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