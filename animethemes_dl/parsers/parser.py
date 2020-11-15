"""
Parses data from myanimelist/anilist and themes.moe.
"""
from ..models import Themes
from ..options import OPTIONS
from .anilist import get_anilist
from .animethemes import get_animethemes
from .myanimelist import get_mal

def combine_themes(animelist: list, themes: list) -> Themes:
    """
    Combines an animelist with themes.
    """
    out = []
    themes = {theme['animelist']['malid']:theme for theme in themes}
    for anime in animelist:
        malid = anime['malid']
        if malid in themes:
            if not (
                OPTIONS['animelist']['minscore'] <= anime['score'] and 
                OPTIONS['animelist']['minpriority'] <= anime['priority']
            ):
                continue
            out.append(themes[malid])
            out[-1]['animelist'].update(anime)
    
    if OPTIONS['download']['sort'] is None:
        return out
    else:
        return sorted(out,
            key=lambda x: x['animelist'][OPTIONS['download']['sort']]
        )

def get_themes(username: str, anilist: bool=False, **animelist_args) -> Themes:
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
