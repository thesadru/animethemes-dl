import requests
import json
import time

THEMESURL = 'https://animethemes-api.herokuapp.com/api/v1/'
MALURL = 'https://myanimelist.net/animelist/{user}/load.json'

def themes_get(*args):
    url = THEMESURL+'/'.join(map(str,args))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def themes_get_mal(username):
    data = themes_get('mal',username)
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
                
        data[i]["short_title"] = (
            theme["mirrors"][0]["mirror"][30:].split('-')[0])
        data[i]['themes'] = [*new_themes.values()]
            
    return data
    

def mal_get_short(username,**kwargs):
    url = MALURL.format(user=username)+'?'
    url = url + '&'.join(k+'='+str(v) for k,v in kwargs.items())
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def mal_get_single(username,**kwargs):
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
    out = []
    for i in range(0,7):
        kwargs['status'] = i
        out.append(mal_get_single(username,**kwargs))
    return out
    

def get_proper_mal(username,**mal_kwargs):
    list_data = mal_get(username,**mal_kwargs)
    themes_data = themes_get_mal(username)
    
    mal_dict = {} # {12345:{'mal_data':{...},'status':1},...}
    for status,animes in enumerate(list_data):
        for anime in animes:
            mal_dict[anime['anime_id']] = {'mal_data':anime,'status':status}
            
    mal_list = [[] for i in range(0,7)]
    for anime in themes_data:
        status   = mal_dict[anime['mal_id']]['status']
        mal_data = mal_dict[anime['mal_id']]['mal_data']
        anime['mal_data'] = mal_data
        mal_list[status].append(anime)
    
    return mal_list
        
    
if __name__ == '__main__':   
    x = get_proper_mal('sadru')
    with open('animethemes-dl.save.json','w') as file:
        json.dump(x,file,indent=4)
