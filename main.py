from pySmartDL import SmartDL
import time;start = time.time()
import os
import json
import subprocess
import string
import eyed3
import requests
from animethemes import get_proper_mal

FILENAME_BAD = set('#%&{}\\<>*?/$!\'":@+`|')
FILENAME_BANNED = set('<>:"/\\|?*')

def generate_filename(anime_name,song_name,theme_type,filetype='.webm'):
    """
    generate a filename
    <anime_name> <OP/ED> (<song_name>).webm
    """
    return f"{anime_name} {theme_type} ({song_name}){filetype}"

def remove_bad_chars(s):
    r = ''
    for i in s:
        if i not in FILENAME_BANNED:
            r += i
    return r

def parse_download_data(anime_data):
    fil_anititle = remove_bad_chars(anime_data["short_title"])
    for theme in anime_data["themes"]:
        mirror = theme["mirrors"][0]
        mirrors = [i["mirror"] for i in theme["mirrors"]]
        url = mirror["mirror"]
        tags = mirror["quality"].split(', ')
        fil_thetitle = remove_bad_chars(theme["title"])
        filename = generate_filename(
            fil_anititle,fil_thetitle,theme["type"])
        
        yield {
            "filename":filename,
            "mirrors":mirrors,
            "metadata":{
                "title":theme["title"],
                "album":anime_data["title"],
                "year":anime_data["year"],
                "genre":145
            }
        }

def get_download_data(username,mal_args={},statuses=[1,2]):
    # [{"filename":"...","mirrors":[...],"metadata":{...}},...]
    out = []
    data = get_proper_mal(username,**mal_args)
    for status in statuses:
        for anime in data[status]:
            for theme in parse_download_data(anime):
                theme["metadata"]["cover art"] = anime["cover"]
                out.append(theme)
    return out

def convert_ffmpeg(webm_filename,mp3_filename=None,save_folder=None):
    """
    convert a webm file to mp3
    """
    if mp3_filename is None:
        mp3_filename = webm_filename[:-5]
    if save_folder is not None:
        mp3_filename = os.path.join(save_folder,os.path.basename(mp3_filename))
    mp3_filename += '.mp3'
    os.system(r'ffmpeg ' + f'-i "{webm_filename}" "{mp3_filename}" -y -c:a libmp3lame -b:a 128k -v quiet -stats -loglevel panic')
    return mp3_filename
    

def add_metadata(path,metadata):
    audiofile = eyed3.load(path)
    if (audiofile.tag == None):
        audiofile.initTag()
    
    audiofile.tag.album = metadata["album"]
    audiofile.tag.title = metadata["title"]
    audiofile.tag.year = metadata["year"]
    image = requests.get(metadata["cover art"]).text.encode()
    audiofile.tag.images.set(3, image, 'image/jpeg')
    #audiofile.tag.genre.set(145)

    audiofile.tag.save()

def download_theme(theme_data,webm_folder=None,mp3_folder=None):
    if webm_folder is None:
        filename = os.path.join(mp3_folder,theme_data["filename"])
    else:
        filename = os.path.join(webm_folder,theme_data["filename"])
    obj = SmartDL(theme_data["mirrors"],filename)
    obj.start()
    dest = obj.get_dest()
    if mp3_folder is not None:
        mp3dest = convert_ffmpeg(dest,save_folder=mp3_folder)
        add_metadata(mp3dest,theme_data["metadata"])
    if webm_folder is None:
        os.remove(dest)
    
    return {"mp3":mp3dest,"webm":dest}


if __name__ == "__main__":
    x = get_download_data('sadru')
    with open('animethemes-dl.json','w') as file:
        json.dump(x,file,indent=4)
    
    x = download_theme(x[0],mp3_folder='mp3_folder')
    print(x)
