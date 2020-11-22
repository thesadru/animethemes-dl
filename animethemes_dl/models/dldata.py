"""
Download data and metadata data types.
"""
from os import PathLike
from typing import List, Optional, TypedDict

from .literals import UrlLike


class Metadata(TypedDict):
    album: str
    disc: str
    year: int
    cover: UrlLike
    track: int
    title: str
    artists: List[str]
    themetype: str
    version: int
    notes: str
    resolution: int
    genre: List[int]
    encodedby: str

class DownloadInfo(TypedDict):
    malid: int

class DownloadData(TypedDict):
    url: UrlLike
    video_path: Optional[PathLike]
    audio_path: Optional[PathLike]
    metadata: Metadata
    info: DownloadInfo

