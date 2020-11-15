from os import PathLike
from .literals import Score,Priority,Status
from typing import Optional,List,TypedDict

_TAGS_TUPLES = [('nocredits','NC'),('lyrics','Lyrics'),('bluray','BD'),
                ('DVD','DVD'),('1080','1080'),('480','480')]
_NOTE_TUPLES = [('spoilers','Spoilers'),('nsfw','NSFW')]

class AnimeListOptions(TypedDict):
    username: str
    anilist: bool
    animelist_args: dict
    minpriority: Priority
    minscore: Score

FilterOptions = TypedDict(
    'FilterOptions',
    {
        **{k:bool  for k,t in _NOTE_TUPLES},# type: ignore
        **{k:bool for k,t in _TAGS_TUPLES}  # type: ignore
    }
)

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
    add_coverart: bool
    coverart_folder: Optional[PathLike]
    timeout: int
    retries: int
    sort: str
    compression: CompressionOptions

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
        'spoilers': True,
        'nsfw': True,
        'nocredits': False,
        'lyrics': False,
        'bluray': False,
        'DVD': False,
        '1080': False,
        '480': False
    },
    'download': {
        'filename':'%(short_anime_title)s-%(type)s.%(filetype)s',
        'audio_folder':None,
        'video_folder':None,
        'no_redownload':False,
        'ascii':False,
        'add_coverart':False,
        'coverart_folder': None,
        'timeout':5,
        'retries':3,
        'sort':None,
        'compression':{
            'root_dir':None,
            'base_name':'animethemes',
            'format':'tar',
            'base_dir':None
        }
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
        open('settings.json','w'),
        indent=4,
        allow_nan=True
    )
