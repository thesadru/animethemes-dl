"""
Download data and metadata data types.
"""
from os import PathLike
from typing import List, Literal, Optional, TypedDict

from .literals import StrInt, UrlLike


class Metadata(TypedDict):
    title: str
    album: str
    genre: List[int]
    coverart: UrlLike
    encodedby: Literal['animethemes.moe']
    version: StrInt
    discnumber: StrInt

class ADownloadData(TypedDict):
    url: UrlLike
    video_path: Optional[PathLike]
    audio_path: Optional[PathLike]
    metadata: Metadata

DownloadData = List[ADownloadData]
