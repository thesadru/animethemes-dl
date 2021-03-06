"""
Normalized AnimeList type.
"""
from datetime import datetime
from typing import Literal, Tuple, TypedDict


class AnimeListDict(TypedDict):
    title: str
    malid: int
    status: Literal[1,2,3,4,6]
    score: Literal[0,1,2,3,4,5,6,7,8,9,10]
    priority: Literal[0,1,2]
    start_date: datetime

AnimeListSite = str
AnimeListEntry = Tuple[str,int,AnimeListSite]