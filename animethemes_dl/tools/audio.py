"""
Audio tools.
Includes ffmpeg conversion and id3 tagging.
"""
import logging
from mimetypes import guess_type
from os import PathLike, system, listdir
from os.path import basename, isfile, join
from typing import Optional, Tuple

import requests
from mutagen.id3 import ID3, ID3TimeStamp
import mutagen.id3._frames as frames

from ..errors import FfmpegException
from ..models import Metadata
from ..options import OPTIONS
from pySmartDL.utils import get_random_useragent

logger = logging.getLogger('animethemes-dl')

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
        raise FfmpegException('Ffmpeg failed to convert.')

def find_file(s: str, directory: str='.') -> Optional[PathLike]:
    """
    Goes through all files in directory and returns one that contains `s`.
    """
    for path in listdir(directory):
        if s in path:
            return join(directory,path)
    return None

def get_coverart(metadata: Metadata, malid: int) -> Tuple[bytes,str,str]:
    """
    Gets coverart, description and mime type for an mp3 file.
    """
    coverart_folder = OPTIONS['coverart']['folder']
    resolution = OPTIONS['coverart']['resolution']-1
    coverart_file = join(coverart_folder,str(malid)+'.png')
    
    if coverart_folder and isfile(coverart_file):
        with open(coverart_file,'rb') as file:
            data = file.read()
        mimetype = guess_type(coverart_file)[0]
    else:
        url = metadata['coverarts'][min(resolution, len(metadata['coverarts'])-1)]
        data = requests.get(url,headers={'User-Agent':get_random_useragent()}).content
        mimetype = guess_type(url)[0]
        if coverart_folder:
            with open(coverart_file,'wb') as file:
                file.write(data)
    
    desc = f'{malid}-{resolution}'
    return data,desc,mimetype

def add_id3_metadata(path: PathLike, metadata: Metadata, malid: int=None):
    """
    Adds metadata to an MP3 file using mutagens `EasyID3`.
    Uses ID3 v2.4.
    If no malid is given, coverart cannot be added.
    """
    logger.info(f"[tag] Adding metadata{' (w/coverart) 'if OPTIONS['coverart']['folder'] else' '}for {basename(path)}")
    audio = ID3(path)
    audio.clear()
    audio.add(frames.TALB(text=metadata['album']))
    # audio.add(TPOS(text=metadata['disc'])) # I want the series, but audio players want an integer. put off for now
    audio.add(frames.TDRC(text=[ ID3TimeStamp(str(metadata['year'])) ]))
    audio.add(frames.TRCK(text=str(metadata['track']))) # useless since there's no discs, I'll keep anyways.
    audio.add(frames.TIT2(text=metadata['title']))
    # audio.add(TPE2(text=metadata['artists'])) # ID3 is not made for singers, doesn't have a tag (TPE1 and TPE2 are wrong)
    audio.add(frames.TXXX(text=metadata['series'],desc='series'))
    audio.add(frames.TXXX(text=metadata['themetype'],desc='themetype'))
    audio.add(frames.TXXX(text=str(metadata['version']),desc='version'))
    audio.add(frames.TXXX(text=str(metadata['videoid']),desc='videoid'))
    audio.add(frames.TXXX(text=metadata['notes'],desc='notes'))
    audio.add(frames.TCON(text=metadata['genre']))
    audio.add(frames.TENC(text=metadata['encodedby']))
    audio.add(frames.TIT1(text=metadata['cgroup']))
    if malid is not None and OPTIONS['coverart']['folder']:
        coverart,desc,mimetype = get_coverart(metadata,malid)
        audio.add(frames.APIC(encoding=3,mime=mimetype,desc=desc,type=3,data=coverart))
    
    audio.save(v2_version=OPTIONS['id3v2_version'])

if __name__ == "__main__":
    import sys
    audio = ID3(sys.argv[1])
    print('showing ID3 informations for ',sys.argv[1])
    print(audio.pprint())
