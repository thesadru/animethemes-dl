"""
Parses data from myanimelist/anilist and themes.moe.
Mostly just a dummy file, that holds a single functions.
"""
from typing import List

from ..models import AnimeThemeAnime, AnimeListSite
from .animelist import ANIMELISTSITES
from .animethemes import fetch_animethemes


def get_animethemes(username: str, site: AnimeListSite, **animelist_kwargs) -> List[AnimeThemeAnime]:
    """
    Gets data from themes.moe and myanimelist.net/anilist.co.
    Returns a dictionary of anime themes.
    To use anilist.co instead of myanimelist.net, use `anilist`.
    For additional args for myanimelist/anilist, use `animelist_args`.
    """
    animelist = ANIMELISTSITES[site]
    titles = animelist(**animelist_kwargs).get_titles(username)
    return fetch_animethemes(titles)
