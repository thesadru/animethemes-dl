import logging
import mimetypes
from mimetypes import guess_extension, guess_type
from os import PathLike, system
from os.path import basename, isfile, join, split, splitext
from typing import Tuple

import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

from ..errors import FfmpegException
from ..options import OPTIONS
from ..models import Metadata,UrlLike

logger = logging.getLogger(__name__)

def ffmpeg_convert(old: str, new: str):
    """
    Convert a video file to an audio file with ffmpeg.
    Uses an `old` path and converts into `new` path.
    """
    loglevel = 'quiet' if OPTIONS['quiet'] else 'warning'
    ffmpeg_command = f' -i "{old}" "{new}" -y -stats -v quiet -loglevel {loglevel}'
    
    logger.debug(f'running ffmpeg cmd "{ffmpeg_command}".')
    
    system(OPTIONS['ffmpeg']+ffmpeg_command)
    if not isfile(new):
        logger.error(f'ffmpeg failed to convert "{old}" to "{new}".')
        raise FfmpegException('Ffmpeg failed to convert, check if in path.')

def get_coverart(url: UrlLike, metadata: Metadata=None) -> Tuple[bytes,str,str]:
    """
    Gets coverart for an mp3 file, it's description and it's mime type.
    """
    
    if url.count('?s='):
        mimetype = guess_type(url.split('?')[0])[0] # MAL has access tokens, so we need to get only the url
        desc = 'Coverart from "myanimelist.net"'
    else:
        mimetype = guess_type(url)[0]
        desc = 'Coverart from "anilist.co"'
    
    if OPTIONS['download']['coverart_folder'] is None or metadata is None:
       return requests.get(url).content,desc,mimetype
    
    coverart_filename = basename(splitext(metadata['discnumber'])[0]) + guess_extension(mimetype)
    coverart_path = join(OPTIONS['download']['coverart_folder'],coverart_filename)
    
    if isfile(coverart_path):
        data = open(coverart_path,'rb').read()
    else:
        data = requests.get(url).content
        open(coverart_path,'wb').write(data)
    
    return data,desc,mimetype

def add_id3_coverart(filename: PathLike, url: UrlLike, metadata: Metadata=None, apictype: int=3):
    """
    Adds coverart to an mp3 file.
    You can set exact apictype, front cover by default.
    Can save to a file with `coverart_filename`.
    """
    audio = ID3(filename)
    coverart,desc,mimetype = get_coverart(url,metadata)
    audio.add(
        APIC(
            encoding=3,
            mime=mimetype,
            desc=desc,
            type=apictype,
            data=coverart
        )
    )
    audio.save()

def add_id3_metadata(path: PathLike, metadata: Metadata, add_coverart: bool=False):
    """
    Adds metadata to an MP3 file using mutagens `EasyID3`.
    Uses ID3 v2.4.
    """
    logger.info(f'[tag] Adding metadata for {path} (coverart={int(add_coverart)})')
    coverart = metadata.pop('coverart')
    audio = EasyID3(path)
    audio.update(metadata)
    audio.save()
    
    if add_coverart:
        add_id3_coverart(path, coverart, metadata)

if __name__ == "__main__":
    import sys
    audio = ID3(sys.argv[1])
    print('showing ID3 informations for ',sys.argv[1])
    print(audio.pprint())
