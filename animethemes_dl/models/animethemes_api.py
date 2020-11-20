from typing import Literal, NewType, Dict, TypedDict, List
from .literals import UrlLike

DateLike = NewType('datetime',str)
Types = Literal['OP','ED']
Seasons = Literal['Spring','Summer','Fall','Winter']

class AnimeThemeDict(TypedDict):
    id: int
    created_at: DateLike
    updated_at: DateLike
    links: TypedDict('links',{'show':UrlLike})

class AnimeThemeSynonym(AnimeThemeDict):
    text: str

class AnimeThemeArtist(AnimeThemeDict):
    name: str
    slug: str
    as_: str

class AnimeThemeSong(AnimeThemeDict):
    title: str
    artists: List[AnimeThemeArtist]

class AnimeThemeVideo(AnimeThemeDict):
    basename: str
    filename: str
    path: str
    size: int
    resolution: int
    nc: bool
    subbed: bool
    lyrics: bool
    uncen: bool
    source: str
    overlap: str
    link: UrlLike

class AnimeThemeEntry(AnimeThemeDict):
    version: str
    episodes: str
    nsfw: bool
    spoiler: bool
    notes: str
    videos: List[AnimeThemeVideo]

class AnimeThemeTheme(AnimeThemeDict):
    type: Types
    sequence: str
    group: str
    slug: str
    song: AnimeThemeSong
    entries: List[AnimeThemeEntry]

class AnimeThemeSerie(AnimeThemeDict):
    name: str
    slug: str

class AnimeThemeResource(AnimeThemeDict):
    link: UrlLike
    external_id: int
    site: str
    as_: str

class AnimeThemeAnime(AnimeThemeDict):
    name: str
    slug: str
    year: int
    season: Seasons
    synopsis: str
    cover: str
    synonyms: List[AnimeThemeSynonym]
    themes: List[AnimeThemeTheme]
    series: List[AnimeThemeSerie]
    resources: List[AnimeThemeResource]

if __name__ == "__main__":
    from ..parsers.animethemes_api import get_animelist
    from ..parsers.myanimelist import get_mal
    animelist = get_animelist([ get_mal('sadru')[0] ])
    print(animelist[0]['themes'][0]['entries'][0]['videos'][0]['links']['show'])