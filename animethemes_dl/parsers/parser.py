"""
Parses data from myanimelist/anilist and themes.moe.
"""
from typing import List
from animethemes_dl.options import OPTIONS
import logging

from ..models.animethemes import AnimeThemeAnime
from .anilist import get_anilist
from .animethemes import fetch_animethemes
from .myanimelist import get_mal

logger = logging.getLogger('animethemes-dl')

def get_animethemes(username: str, anilist: bool=False, **animelist_args) -> List[AnimeThemeAnime]:
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
    return fetch_animethemes(animelist)

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_animethemes('sadru'))
