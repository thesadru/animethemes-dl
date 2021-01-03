"""
Animethemes ap model.
Copied from the flowchart the dev posted in discord.
"""
from typing import List, Literal, NewType, TypedDict, Union


class AnimeThemeDict(TypedDict):
    id: int
    created_at: str
    updated_at: str

class AnimeThemeLinkable(AnimeThemeDict):
    link: str

class AnimeThemeSynonym(AnimeThemeDict):
    text: str

class AnimeThemeArtist(AnimeThemeDict):
    name: str
    slug: str
    as_: str

class AnimeThemeSong(AnimeThemeDict):
    title: str
    artists: List[AnimeThemeArtist]

class AnimeThemeVideo(AnimeThemeLinkable):
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

class AnimeThemeEntry(AnimeThemeDict):
    version: Union[int,Literal['']]
    episodes: str
    nsfw: bool
    spoiler: bool
    notes: str
    videos: List[AnimeThemeVideo]

class AnimeThemeTheme(AnimeThemeDict):
    type: Literal['OP','ED']
    sequence: str
    group: str
    slug: str
    song: AnimeThemeSong
    entries: List[AnimeThemeEntry]

class AnimeThemeSerie(AnimeThemeDict):
    name: str
    slug: str

class AnimeThemeResource(AnimeThemeLinkable):
    external_id: int
    site: str
    as_: str

class AnimeThemeImage(AnimeThemeLinkable):
    path: str
    facet: Literal['Large Cover', 'Small Cover']

class AnimeThemeAnime(AnimeThemeDict):
    name: str
    slug: str
    year: int
    season: Literal['Spring','Summer','Fall','Winter']
    synopsis: str
    synonyms: List[AnimeThemeSynonym]
    themes: List[AnimeThemeTheme]
    series: List[AnimeThemeSerie]
    resources: List[AnimeThemeResource]
    images: List[AnimeThemeImage]
    
    _fetched_at: int

if __name__ == "__main__":
    from ..parsers.animethemes import fetch_animethemes
    from ..parsers.myanimelist import get_mal
    animelist = fetch_animethemes([ get_mal('sadru')[0] ])
    print(animelist[0]['themes'][0]['entries'][0]['videos'][0]['links']['show'])
