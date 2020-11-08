"""
Parses data from myanimelist/anilist and themes.moe.
"""
from .anilist import get_anilist
from .myanimelist import get_mal
from .animethemes import get_themes

def animelist_to_dict(animelist: dict) -> dict:
    """
    Turns an edited animelist into a dict of {malid:data}.
    """
    out = {i:{} for i in range(1,7)}
    for status in animelist:
        for anime in animelist[status]:
            out[status][anime['malid']] = anime
    return out

def combine_themes(animelist: dict, themes: list) -> dict:
    """
    Combines an animelist with themes.
    """
    out = {i:[] for i in range(1,7)}
    animelist = animelist_to_dict(animelist)
    for theme in themes:
        malid = theme['malid']
        status = theme['status']
        if malid not in animelist[status]:
            continue
        data = animelist[status][malid]
        data['year'] = theme['year']
        data['season'] = theme['season']
        theme = theme['themes']
        
        out[status].append({
            'themes':theme,
            'animelist':data
        })
    return out

def get_animethemes(username: str, anilist: bool=False, **animelist_args) -> dict:
    """
    Gets data from themes.moe and myanimelist.net/anilist.co.
    Returns a dictionary of anime themes split into it's current status.
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    if anilist:
        animelist = get_anilist(username, **animelist_args)
    else:
        animelist = get_mal(username, **animelist_args)
    themes = get_themes(username)
    return combine_themes(animelist,themes)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_animethemes('sadru'))