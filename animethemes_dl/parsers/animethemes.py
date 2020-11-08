"""
Gets data from themes.moe using their API.
"""
import requests

THEMESURL = 'https://themes.moe/api/mal/{user}'
POSSIBLETAGS = [
    'NC',
    'Subbed',
    'Lyrics',
    'Cen',
    'Uncen',
    '60FPS',
    'Trans',
    'BD',
    '420',
    '720',
    '1080'
]
POSSIBLENOTES = [
    'Spoiler',
    'NSFW'
]

def get_tags(s: str, possible: list=POSSIBLETAGS) -> list:
    """
    Gets tags from a url
    """
    tags = []
    for tag in possible:
        if tag in s:
            tags.append(tag)
    return tags

def parse_theme_type(themetype: str) -> tuple:
    """
    Parser a themetype into a `(type, short type, version)` tuple.
    """
    themetype = themetype.split()
    if len(themetype) == 1:
        themetype = themetype[0]
        version = 1
    else:
        themetype,version = themetype
        version = int(version[1:])
    
    shortype = themetype[:2]
    return themetype,shortype,version
    

def get_raw_themes(username: str) -> list:
    """
    Gets themes from r/animethemes using the themes.moe api.
    """
    url = THEMESURL.format(user=username)
    
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def sort_themes(data: list, only_mirrors: bool = False) -> dict:
    """
    Sorts themes and returns a version used for animethemes-dl.
    """
    out = []
    for entry in data:
        themes = {}
        for theme in entry['themes']:
            themetype,shortype,version = parse_theme_type(theme['themeType'])
            mirror = theme['mirror']
            url = mirror['mirrorURL']
            tags = get_tags(url)
            notes = get_tags(mirror['notes'],POSSIBLENOTES)
            
            if themetype not in themes:
                short_name = url.split('/')[-1].split('-')[0]
                themes[themetype] = {
                    'name':theme['themeName'],
                    'short_name': short_name,
                    'type': themetype,
                    'shortype':shortype,
                    'mirrors':[]
                }
            
            themes[themetype]['mirrors'].append({
                'url': url,
                'version':version,
                'tags': tags,
                'notes': notes,
                'priority': mirror['priority'],
            })
        sorted_themes = []
        for theme in themes.values():
            theme['mirrors'].sort(key=lambda mirror: mirror['priority'])
            sorted_themes.append(theme)
        
        out.append({
            'malid':entry['malID'],
            'status':entry['watchStatus'],
            'year':entry['year'],
            'season': entry['season'],
            'themes': sorted_themes
        })
    
    return out

def get_themes(username: str) -> list:
    """
    Gets themes with a username.
    """
    raw = get_raw_themes(username)
    return sort_themes(raw)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_themes('sadru'))

