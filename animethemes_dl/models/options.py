from os import PathLike
from .literals import Score,Priority,Status
from typing import Optional,List,TypedDict,Callable

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

class DownloadOptions(TypedDict):
    filename: str
    audio_folder: Optional[PathLike]
    video_folder: Optional[PathLike]
    no_redownload: bool
    ascii: bool
    add_coverart: bool
    coverart_folder: Optional[PathLike]
    retries: int
    sort: Callable

class Options(TypedDict):
    animelist: AnimeListOptions
    filter: FilterOptions
    download: DownloadOptions
    statuses: List[Status]
    quiet: bool
    ffmpeg: PathLike

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
        'retries':3,
        'sort':lambda _: 0
    },
    'statuses':[1,2],
    'quiet': False,
    'ffmpeg': 'ffmpeg'
}