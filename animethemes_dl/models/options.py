"""
Option data type and option defaults.
"""
from os import PathLike
from typing import Optional,List,Tuple,TypedDict,Literal
from .animelist import AnimeListSite

class AnimeListOptions(TypedDict):
    username: str
    site: AnimeListSite
    animelist_args: dict
    minpriority: Literal[0,1,2]
    minscore: Literal[0,1,2,3,4,5,6,7,8,9,10]
    range: Tuple[int,int]

class FilterOptions(TypedDict):
    smart: bool
    no_copy: bool
    type: Literal['OP','ED',None]
    spoiler: Optional[bool]
    nsfw: Optional[bool]
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
    update: bool
    ascii: bool
    timeout: int
    retries: int
    max_cache_age: int
    force_videos: List[int]

class Options(TypedDict):
    animelist: AnimeListOptions
    filter: FilterOptions
    download: DownloadOptions
    statuses: List[Literal[1,2,3,4,6]]
    coverart: CoverartOptions
    compression: CompressionOptions
    quiet: bool
    no_colors: bool
    ffmpeg: PathLike
    id3v2_version: Literal[3,4]
    ignore_prompts: bool
