"""
Option data type and option defaults.
"""
from os import PathLike
from .literals import Score,Priority,Status
from typing import Optional,List,TypedDict,Literal

class AnimeListOptions(TypedDict):
    username: str
    anilist: bool
    animelist_args: dict
    minpriority: Priority
    minscore: Score

class EntryFilterOptions(TypedDict):
    spoiler: Optional[bool]
    nsfw: Optional[bool]

class FilterOptions(TypedDict):
    entry: EntryFilterOptions
    resolution: int
    nc: Optional[bool]
    subbed: Optional[bool]
    lyrics: Optional[bool]
    uncen: Optional[bool]
    source: Optional[str]
    overlap: Optional[str]

class CoverartOptions(TypedDict):
    resolution: Literal[0,1,2,3]
    folder: Optional[PathLike]

class CompressionOptions(TypedDict):
    root_dir: Optional[PathLike]
    base_name: str
    format: str
    base_dir: Optional[PathLike]

class DownloadOptions(TypedDict):
    filename: str
    audio_folder: Optional[PathLike]
    video_folder: Optional[PathLike]
    no_redownload: bool
    ascii: bool
    timeout: int
    retries: int
    sort: str
    coverart: CoverartOptions
    compression: CompressionOptions
    force_videos: List[int]

class Options(TypedDict):
    animelist: AnimeListOptions
    filter: FilterOptions
    download: DownloadOptions
    statuses: List[Status]
    quiet: bool
    no_colors: bool
    ffmpeg: PathLike
    ignore_prompts: bool

DEFAULT = {
    'animelist': {
        'username': '',
        'anilist': False,
        'animelist_args': {},
        'minpriority':0,
        'minscore':0
    },
    'filter': {
        'entry': {
            'spoiler': None,
            'nsfw': None
        },
        'resolution':0,
        'nc': None,
        'subbed': None,
        'lyrics': None,
        'uncen': None,
        'source': None,
        'overlap': None
    },
    'download': {
        'filename':'%(anime_filename)s-%(theme_slug)s.%(video_filetype)s',
        'audio_folder':None,
        'video_folder':None,
        'no_redownload':False,
        'ascii':False,
        'timeout':5,
        'retries':3,
        'coverart':{
            'resolution':0,
            'folder': None,
        },
        'compression':{
            'root_dir':None,
            'base_name':'animethemes',
            'format':'tar',
            'base_dir':None
        },
        'force_videos': []
    },
    'statuses':[1,2],
    'quiet': False,
    'no_colors':False,
    'ffmpeg': 'ffmpeg',
    'ignore_prompts': False
}

if __name__ == "__main__":
    import json
    json.dump(
        DEFAULT,
        open('hints/settings.json','w'),
        indent=4,
        allow_nan=True
    )
