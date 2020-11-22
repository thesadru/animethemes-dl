"""
Audio tools.
Includes ffmpeg conversion and id3 tagging.
"""
import logging
from mimetypes import guess_extension, guess_type
from os import PathLike, system, listdir
from os.path import basename, isfile, join, splitext
from typing import Optional, Tuple

import requests
from mutagen.id3 import ID3, ID3TimeStamp
from mutagen.id3._frames import *

from ..errors import FfmpegException
from ..models import Metadata, UrlLike
from ..options import OPTIONS
from ..parsers.anilist import ALURL

logger = logging.getLogger('animethemes-dl')

COVERARTQUERY = """
query Media($malid: Int) {
  Media(idMal: $malid type: ANIME) {
    idMal
    coverImage {
      extraLarge
      large
      medium
      # color
    }
  }
}
"""

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

def fetch_coverart(malid: int, size:int, query: str=COVERARTQUERY, **variables) -> str:
    """
    Returns a coverart url of 1-3 resolution.
    """
    variables['malid'] = int(malid)
    json_arg = {'query':query, 'variables':variables}
    
    r = requests.post(ALURL,json=json_arg)
    if r.status_code == 200:
        data = r.json()
    else:
        return r.raise_for_status()
    
    covers = data['data']['Media']['coverImage']
    return covers[{
        0:'medium', # prevents some stupid bugs
        1:'medium',
        2:'large',
        3:'extraLarge'
    }[size]]

def find_file(s: str, directory: str='.') -> Optional[PathLike]:
    """
    Goes through all files in directory and returns one that contains `s`.
    """
    for path in listdir(directory):
        if s in path:
            return join(directory,path)

def get_coverart(malid: int) -> Tuple[bytes,str,str]:
    """
    Gets coverart, description and mime type for an mp3 file.
    """
    coverart_folder = OPTIONS['download']['coverart']['folder']
    resolution = OPTIONS['download']['coverart']['resolution']
    
    data=None;path=None # my pylance was complaining...
    if coverart_folder:
        path = find_file(str(malid),coverart_folder)
        if path:
            data = open(path,'rb').read()
    
    if data is None:
        logger.debug(f'Fetching coverart for {malid} ({resolution})')
        url = fetch_coverart(malid,resolution)
        data = requests.get(url).content
        path = join(coverart_folder,str(malid)+splitext(url)[1])
        if coverart_folder:
            open(path,'wb').write(data)
    
    logger.debug(f'Added coverart {malid} ({len(data)}B).')
    
    mimetype = guess_type(path)
    desc = f"{malid}, resolution {resolution}/3"
    
    return data,desc,mimetype

def add_id3_metadata(path: PathLike, metadata: Metadata, malid: int=None):
    """
    Adds metadata to an MP3 file using mutagens `EasyID3`.
    Uses ID3 v2.4.
    If no malid is given, coverart cannot be added.
    """
    logger.info(f"[tag] Adding metadata{' (w/coverart) 'if OPTIONS['download']['coverart']['folder'] else' '}for {basename(path)}")
    audio = ID3(path)
    audio.clear()
    audio.add(TALB(text=metadata['album']))
    # audio.add(TPOS(text=metadata['disc'])) # I want the series, but audio players want an integer. put off for now
    audio.add(TDRC(text=[ ID3TimeStamp(str(metadata['year'])) ]))
    audio.add(TRCK(text=str(metadata['track']))) # useless since there's no discs, I'll keep anyways.
    audio.add(TIT2(text=metadata['title']))
    # audio.add(TPE2(text=metadata['artists'])) # ID3 is not made for singers, doesn't have a tag (TPE1 and TPE2 are wrong)
    audio.add(TXXX(text=metadata['series'],desc='series'))
    audio.add(TXXX(text=metadata['themetype'],desc='themetype'))
    audio.add(TXXX(text=str(metadata['version']),desc='version'))
    audio.add(TXXX(text=metadata['notes'],desc='notes'))
    audio.add(TCON(text=metadata['genre']))
    audio.add(TENC(text=metadata['encodedby']))
    audio.add(TIT1(text=metadata['cgroup']))
    if malid is not None and OPTIONS['download']['coverart']['folder']:
        coverart,desc,mimetype = get_coverart(malid)
        audio.add(APIC(encoding=3,mime=mimetype,desc=desc,type=3,data=coverart))
    
    audio.save()

if __name__ == "__main__":
    import sys
    audio = ID3(sys.argv[1])
    print('showing ID3 informations for ',sys.argv[1])
    print(audio.pprint())
