"""
Audio tools.
Includes ffmpeg conversion and id3 tagging.
"""
import logging
from mimetypes import guess_extension, guess_type
from os import PathLike, system, listdir
from os.path import basename, isfile, join, splitext
from typing import Tuple

import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
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
        raise FfmpegException('Ffmpeg failed to convert, check if in path.')

def fetch_coverart(malid: int, size:int, query:str=COVERARTQUERY, **variables) -> str:
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
        1:'medium',
        2:'large',
        3:'extraLarge'
    }[size]]

def get_coverart(url: UrlLike, metadata: Metadata=None) -> Tuple[bytes,str,str]:
    """
    Gets coverart for an mp3 file, it's description and it's mime type.
    """
    coverart_folder = OPTIONS['download']['coverart']['folder']
    resolution = OPTIONS['download']['coverart']['resolution']
    malid = metadata['discnumber']
    
    path = None; data = None
    
    if coverart_folder:
        for path in listdir(coverart_folder):
            if malid in path:
                path = join(coverart_folder,path)
                data = open(path,'rb').read()
    
    if data is None:
        if resolution > 1:
            logger.debug(f'Fetching coverart for {malid} ({resolution})')
            url = fetch_coverart(malid,resolution)
        data = requests.get(url).content
        extension = splitext(url.split('?s=')[0])[1]
        path = join(coverart_folder,str(malid)+extension)
        open(path,'wb').write(data)
    
    logger.debug(f'Added coverart of size {len(data)} to {malid}.')
    
    mimetype = guess_type(path)
    desc = f"{malid}, resolution {resolution}/3"
    
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
    logger.info(f"[tag] Adding metadata{' (w/coverart) ' if add_coverart else ' '}for {basename(path)}")
    audio = ID3(path)
    audio.clear()
    audio['TALB'] = TALB(text=metadata['album'])
    audio['TIT2'] = TIT2(text=metadata['title'])
    audio['TIT3'] = TIT3(text=metadata['version'])
    audio['TCON'] = TCON(text=metadata['genre'])
    audio['TENC'] = TENC(text=metadata['encodedby'])
    audio['TPOS'] = TPOS(text=metadata['discnumber'])
    audio.save()
    
    if add_coverart:
        add_id3_coverart(path, metadata['coverart'], metadata)

if __name__ == "__main__":
    import sys
    audio = ID3(sys.argv[1])
    print('showing ID3 informations for ',sys.argv[1])
    print(audio.pprint())
