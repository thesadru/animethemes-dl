"""
Theme data types.
"""
from typing import List, TypedDict

from .animelist import SingleAnimeList
from .animethemes import AnimeTheme


class Theme(TypedDict):
    themes: List[AnimeTheme]
    animelist: SingleAnimeList

Themes = List[Theme]
