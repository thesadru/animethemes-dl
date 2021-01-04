"""
Parses data from myanimelist/anilist and themes.moe.
Mostly just a dummy file, that holds a single functions.
"""
from typing import List
from ..models import AnimeThemeAnime
from .animelist import AniList, MyAnimeList
from .animethemes import fetch_animethemes

def get_animethemes(username: str, anilist: bool=False, **animelist_kwargs) -> List[AnimeThemeAnime]:
    """
    Gets data from themes.moe and myanimelist.net/anilist.co.
    Returns a dictionary of anime themes.
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    if anilist: animelist = AniList
    else:       animelist = MyAnimeList
    titles = animelist(**animelist_kwargs).get_titles(username)
    return fetch_animethemes(titles)
