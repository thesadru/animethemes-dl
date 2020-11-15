"""
AnimeThemes models.
"""
from typing import List, TypedDict

from .literals import Season, UrlLike


class Mirror(TypedDict):
    url: UrlLike
    version: int
    tags: List[str]
    notes: List[str]
    priority: int

class AnimeTheme(TypedDict):
    title: str
    type: str
    shortype: str
    mirrors: List[Mirror]

class SingleAnimeThemeAnimeList(TypedDict):
    malid: int
    status: int
    short_title: str
    year: int
    season: Season

class RawAnimeThemes(TypedDict):
    themes: List[AnimeTheme]
    animelist: SingleAnimeThemeAnimeList
