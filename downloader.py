from pySmartDL import SmartDL
import time;start = time.time()
import os
import sys
import json
import string
import eyed3
from pprint import pprint
import requests
from animethemes import get_proper
from printer import fprint
from globals import Opts

FILENAME_BAD = set('#%&{}\\<>*?/$!\'":@+`|')
FILENAME_BANNED = set('<>:"/\\|?*')
FILENAME_ALLOWEDASCII = set(string.printable).difference(FILENAME_BANNED)

'''
def generate_filename(anime_name,song_name,theme_type,filetype='.webm'):
    """
    generate a filename
    <anime_name> <OP/ED> (<song_name>).webm
    """
    return f"{anime_name} {theme_type} ({song_name}){filetype}"
'''
def generate_filename(
    anime_name_short,anime_name,
    song_name,theme_type,
    filetype='webm'
):
    if Opts.Download.filename:
        filename = Opts.Download.filename
    else:
        filename =  f"%A %t (%S).%e"
    translate = {
        '%':'%',
        'a':anime_name_short,
        'A':anime_name,
        't':theme_type,
        's':song_name.replace(' ','_'),
        'S':song_name,
        'e':filetype
    }
    out = ''
    i = 0
    while i < len(filename):
        if filename[i] == '%':
            out += translate[filename[i+1]]
            i += 2
        else:
            out += filename[i]
            i += 1
    return out
    
    

def to_mal_priority(arg,no_raise=True):
    if arg in {0,1,2}:
        return arg
    elif arg in '012':
        return int(arg)
    try:
        return {
            "low":0,
            "medium":1,
            "high":2
        }[arg.lower()]
    except KeyError:
        return arg

def remove_bad_nonascii(s):
    r = ''
    for i in s:
        if i in FILENAME_ALLOWEDASCII:
            r += i
    return r
            

def remove_bad_chars(s):
    if Opts.Download.ascii:
        return remove_bad_nonascii(s)
    
    r = ''
    for i in s:
        if i not in FILENAME_BANNED:
            r += i
    return r

def parse_download_data(anime_data):
    fil_anititles = remove_bad_chars(anime_data["short_title"])
    fil_anititlel = remove_bad_chars(anime_data["title"])
    for theme in anime_data["themes"]:
        mirror = theme["mirrors"][0]
        url = mirror["mirror"]
        tags = mirror["quality"].split(', ')
        if (
            Opts.Download.sfw and 'NSFW' in theme['notes'] or
            Opts.Download.no_dialogue and 'Trans' in tags
        ):
            continue
        mirrors = [i["mirror"] for i in theme["mirrors"]]
        audio_mirrors = [i["audio"] for i in theme["mirrors"]]
        fil_thetitle = remove_bad_chars(theme["title"])
        filename = generate_filename(
            fil_anititles,fil_anititlel,fil_thetitle,theme["type"])
        
        yield {
            "filename":filename,
            "mirrors":mirrors,
            "audio_mirrors":audio_mirrors,
            "metadata":{
                "title":theme["title"],
                "album":anime_data["title"],
                "year":anime_data["year"],
                "genre":145,
                "coverart":None
            }
        }

def get_download_data(username,statuses=[1,2],anilist=False,mal_args={}):
    # [{"filename":"...","mirrors":[...],"metadata":{...}},...]
    out = []
    data = get_proper(username,anilist,**mal_args)
    fprint('parse','getting download data')
    for status in statuses:
        for anime in data[status]:
            if (anime['mal_data']['score'] < Opts.Animelist.minscore or
                to_mal_priority(anime['mal_data']['priority_string']) < Opts.Animelist.minpriority
            ):
                continue
            for theme,unparsed in zip(parse_download_data(anime),anime['themes']):
                
                theme["metadata"]["cover art"] = anime["cover"]
                out.append(theme)
    return out

def convert_ffmpeg(webm_filename,mp3_filename=None,save_folder=None):
    """
    convert a webm file to a different tyoe
    """
    if mp3_filename is None:
        mp3_filename = webm_filename[:-5]
    if save_folder is not None:
        mp3_filename = os.path.join(save_folder,os.path.basename(mp3_filename))
    mp3_filename += '.'+Opts.Download.audio_format
    loglevel = 'quiet' if Opts.Print.quiet else 'warning'
    ffmpeg_path = Opts.Download.ffmpeg
    os.system(f'{ffmpeg_path} -i "{webm_filename}" "{mp3_filename}" -y -stats -v quiet -loglevel {loglevel}')
    return mp3_filename
    
def add_metadata(path,metadata,add_coverart):
    t = time.time()
    fprint(f'adding metadata for v2.4'+(' with coverart' if add_coverart else ''),end='')
    audiofile = eyed3.load(path)
    if (audiofile.tag == None):
        audiofile.initTag()
    
    audiofile.tag.album = metadata["album"]
    audiofile.tag.title = metadata["title"]
    audiofile.tag.year = metadata["year"]
    if add_coverart:
        image = requests.get(metadata["cover art"]).text.encode()
        audiofile.tag.images.set(3, image, 'image/jpeg')
    audiofile.tag.genre = 145
    
    audiofile.tag.save()
    fprint(' | '+str(int((time.time()-t)*1000))+'ms')

def download_theme(theme_data,webm_folder=None,mp3_folder=None,no_redownload=False):
    # generate a folder to save webm files
    if webm_folder is None:
        filename = os.path.join(mp3_folder,theme_data["filename"])
    else:
        filename = os.path.join(webm_folder,theme_data["filename"])
    exwebm,exmp3 = os.path.isfile(filename),os.path.isfile(os.path.splitext(filename)[0]+'.mp3')
    
    # determine what files are needed
    if no_redownload:
        needmp3 = mp3_folder is not None and not exmp3
        needwebm = (webm_folder is not None and not exwebm) or (needmp3 and not exwebm)
    else:
        needwebm = True
        needmp3 = mp3_folder is not None
    
    # download webm file if file does not exist
    if needwebm:
        fprint('download',theme_data['filename'])
        obj = SmartDL(theme_data["mirrors"],filename,progress_bar=not Opts.Print.quiet)
        try:
            obj.start()
        except Exception as e:
            fprint('error',str(e))
        webm_dest = obj.get_dest()
        remove_webm = True
    else:
        webm_dest = filename
        remove_webm = False
        
    # download mp3 file if file does not exist
    if needmp3:
        mp3dest = convert_ffmpeg(webm_dest,save_folder=mp3_folder)
        add_metadata(mp3dest,theme_data["metadata"],Opts.Download.coverart)
    else:
        mp3dest = None
    
    # delete webm folder is deemed neccesary
    if webm_folder is None:
        if remove_webm:
            os.remove(webm_dest)
        webm_dest = None
    
    return {"mp3":mp3dest,"webm":webm_dest}

def download_theme_audio_server(theme_data,mp3_folder=None,no_redownload=False,data_size=65536):
    # generate a folder to save webm files
    short_filename = os.path.splitext(theme_data["filename"])[0]+'.mp3'
    filename = os.path.join(mp3_folder,short_filename)
    
    
    # download mp3 file if file does not exist
    if not (no_redownload and os.path.isfile(filename)):
        fprint('download',short_filename)
        for mirror in theme_data['audio_mirrors']:
            t = time.time()
            fprint('requesting for a convert from a server',end='')
            
            try:
                r = requests.get(mirror)
                fprint(' | '+str(int((time.time()-t)*1000))+'ms')
                with open(filename, 'wb') as file:
                    for data in r.iter_content(data_size): #64kiB
                        file.write(data)
                fprint('')
                break
            
            except Exception as e:
                fprint('')
                fprint('error',str(e))
                return None
                
        add_metadata(filename,theme_data["metadata"],Opts.Download.coverart)
        return filename
    else:
        return None

def download_multi_theme(download_data,webm_folder=None,mp3_folder=None):
    if webm_folder is None and mp3_folder is None:
        fprint('error','no save folder set')
    if webm_folder and not os.path.isdir(webm_folder):
        os.mkdir(webm_folder)
    if mp3_folder and not os.path.isdir(mp3_folder):
        os.mkdir(mp3_folder)
    
    if Opts.Download.local_convert or webm_folder is not None:
        fprint('progress','started downloading'+(' and converting' if mp3_folder is not None else ''))
        for theme in download_data:
            download_theme(
                theme,webm_folder,mp3_folder,
                Opts.Download.no_redownload)
    else:
        fprint('progress','started downloading audio files')
        for theme in download_data:
            download_theme_audio_server(
                theme,mp3_folder,
                Opts.Download.no_redownload)

def batch_download(
    username,
    statuses=[1,2],
    webm_folder=None,mp3_folder=None,
    anilist=False
):
    fprint('progress','initializing program')
    download_data = get_download_data(username,statuses,anilist)
    download_multi_theme(download_data,webm_folder,mp3_folder)
    fprint('progress','finished downloading')


if __name__ == "__main__":
    pass
    
