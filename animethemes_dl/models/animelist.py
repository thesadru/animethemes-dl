"""
MyanimeList and AniList models.
"""
from typing import List, TypedDict

from .literals import Priority, Score, Season, Status, UrlLike


class SingleRawAnimeList(TypedDict):
    malid: int
    title: str
    status: Status
    score: Score
    priority: Priority
    notes: str
    cover: UrlLike
    episodes: int

class SingleAnimeList(SingleRawAnimeList):
    short_title: str
    year: int
    season: Season

RawAnimeList = List[SingleRawAnimeList]
AnimeList = List[SingleAnimeList]
