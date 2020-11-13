"""
Parses data from myanimelist/anilist and themes.moe.
"""
from .anilist import get_anilist
from .myanimelist import get_mal
from .animethemes import get_animethemes

def animelist_to_dict(animelist: dict) -> dict:
    """
    Turns an edited animelist into a dict of {malid:data}.
    """
    out = {i:{} for i in range(1,7)}
    for status in animelist:
        for anime in animelist[status]:
            out[status][anime['malid']] = anime
    return out

def combine_themes(animelist: list, themes: list) -> list:
    """
    Combines an animelist with themes.
    """
    animelist = {anime['malid']:anime for anime in animelist}
    for i,theme in reversed((*enumerate(themes),)):
        if theme['animelist']['malid'] in animelist:
            themes[i]['animelist'].update(
                animelist[theme['animelist']['malid']]
            )
        else:
            del themes[i]
    
    return themes

def get_themes(username: str, anilist: bool=False, **animelist_args) -> list:
    """
    Gets data from themes.moe and myanimelist.net/anilist.co.
    Returns a dictionary of anime themes.
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    if anilist:
        animelist = get_anilist(username, **animelist_args)
    else:
        animelist = get_mal(username, **animelist_args)
    themes = get_animethemes(username)
    return combine_themes(animelist,themes)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_animethemes('sadru'))