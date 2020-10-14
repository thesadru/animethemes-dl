"""
downloads anime themes
"""
from pySmartDL import SmartDL
import time;start = time.time()
import os
import eyed3
import threading
import requests
import string
from animethemes import get_proper
from printer import fprint
from globals import Opts

FILENAME_BAD = set('#%&{}\\<>*?/$!\'":@+`|')
FILENAME_BANNED = set('<>:"/\\|?*')
FILENAME_ALLOWEDASCII = set(string.printable).difference(FILENAME_BANNED)

def generate_filename(
    anime_name_short,anime_name,
    song_name,theme_type,
    filetype='webm'
):
    """
    genererates a filename based off Opts.Download.filename
    """
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
    """
    converts an arg to mal priority
    0 = Low; 1 = Medium; 2 = High
    """
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
    """
    removes all characters that shouldn't be in a filename and are not ascii
    """
    r = ''
    for i in s:
        if i in FILENAME_ALLOWEDASCII:
            r += i
    return r
            

def remove_bad_chars(s):
    """
    removes all characters that shouldn't be in a filename
    """
    if Opts.Download.ascii:
        return remove_bad_nonascii(s)
    
    r = ''
    for i in s:
        if i not in FILENAME_BANNED:
            r += i
    return r

def parse_download_data(anime_data):
    """
    parses anime data and converts it into download data
    [
        {
            filename,
            mirrors,
            audio_mirrors,
            metadata {...}
        }
    ]
    """
    fil_anititles = remove_bad_chars(anime_data["short_title"])
    fil_anititlel = remove_bad_chars(anime_data["title"])
    for theme in anime_data["themes"]:
        mirror = theme["mirrors"][0]
        url = mirror["mirror"]
        tags = mirror["quality"].split(', ')
        if (
            Opts.Download.sfw and 'NSFW' in theme['notes'] or
            Opts.Download.no_spoilers and 'Spoiler' in theme['notes'] or
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

def get_download_data(username,statuses=[1,2],anilist=False,extra_ids=[],mal_args={}):
    """
    gets download data with a MAL/AniList username, adds extra anime and fiters out unwanted stuff
    """
    # [{"filename":"...","mirrors":[...],"metadata":{...}},...]
    out = []
    data = get_proper(username,anilist,extra_ids,**mal_args)
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
    convert a video file to an audio file with ffmpeg
    """
    if mp3_filename is None:
        mp3_filename = webm_filename[:-5]
    if save_folder is not None:
        mp3_filename = os.path.join(save_folder,os.path.basename(mp3_filename))
    mp3_filename += '.'+Opts.Download.audio_format
    loglevel = 'quiet' if Opts.Print.quiet else 'warning'
    ffmpeg_path = Opts.Download.ffmpeg
    os.system(f'{ffmpeg_path} -i "{webm_filename}" "{mp3_filename}" -y -stats -v quiet -loglevel {loglevel}')
    if not os.path.isfile(mp3_filename):
        fprint('error',"ffmpeg didn't convert, check if it's in path or use --ffmpeg")
        quit()
    return mp3_filename
    
def add_metadata(path,metadata,add_coverart):
    """
    adds metadata to an mp3 file
    returns True if succeeded, False if failed
    """
    if os.path.splitext(path)[1] != 'mp3':
        return False
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
    
    try:
        audiofile.tag.save()
        fprint(' | '+str(int((time.time()-t)*1000))+'ms')
        return True
    except PermissionError as e:
        fprint('error',f"couldn't add metadata: {e}",start='\n')
        return False

def download_theme(theme_data,webm_folder=None,mp3_folder=None,no_redownload=False):
    """
    downloads a theme with given theme data and destination
    """
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
        except KeyboardInterrupt:
            obj.stop()
            os.remove(obj.get_dest()+'.000')
            quit()
        webm_dest = obj.get_dest()
        remove_webm = True
    else:
        webm_dest = filename
        remove_webm = False
    
    # download mp3 file if file does not exist
    if needmp3:
        if not needwebm:
            fprint('convert',theme_data['filename'])
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

_LAST_DOWNLOAD_TIME = 10.0
def download_theme_audio_server(theme_data,mp3_folder=None,no_redownload=False,data_size=65536,timeout=30):
    """
    downloads an audio file from from a server
    the progress bar is completely fake
    
    returns:
    filename (str)
    empty str if no download was made
    None if all downloads failed
    """
    def progress_bar():
        """
        this progress bar is completely fake, but it makes it feel like something is happening so that's cool
        """
        global _LAST_DOWNLOAD_TIME
        START_TIME = time.time()
        last_increment = last_decrement = time.time()
        expected_remain = _LAST_DOWNLOAD_TIME+0.75
        current_time = lambda: time.time() - START_TIME
        def download_string(x,y,r=2):
            x = str(x).split('.')
            y = str(y).split('.')
            x = x[0]+'.'+x[1][:r]
            y = y[0]+'.'+y[1][:r]
            return f'[*] {x}s / {y}s  '

        while True:
            fprint(download_string(current_time(),expected_remain),end='\r')
            
            # time updater
            difference = expected_remain-current_time()
            if difference < 1:
                # never get it too close to the expected remain
                expected_remain += 1
                last_increment = time.time()
            elif time.time() - last_increment > 0.5 and difference < 10:
                # add time to make it look like it's updating
                expected_remain += 1/(expected_remain-current_time())
                last_increment = time.time()
            elif time.time() - last_decrement > 2:
                # remove some time because it feels good to make it faster
                expected_remain -= 2/(expected_remain-current_time())
                last_decrement = time.time()
                
            if STOP_PROGRESS_BAR:
                break
            if current_time() >= timeout:
                fprint('error','download timed out')
                return
        
        if FAKE_COMPLETE:
            fprint(download_string(current_time(),current_time()))
            _LAST_DOWNLOAD_TIME = current_time()
        else:
            fprint('')
        
        
    # generate a folder to save webm files
    short_filename = os.path.splitext(theme_data["filename"])[0]+'.mp3'
    filename = os.path.join(mp3_folder,short_filename)
    
    # download mp3 file if file does not exist
    if not (no_redownload and os.path.isfile(filename)):
        fprint('download',short_filename)
        for mirror in theme_data['audio_mirrors']:
            STOP_PROGRESS_BAR = False
            FAKE_COMPLETE = False
            thread = threading.Thread(target=progress_bar)
            thread.start()
            try:
                r = requests.get(mirror)
            except KeyboardInterrupt:
                STOP_PROGRESS_BAR = True
                thread.join()
                quit()
            except Exception as e:
                fprint('error',e)
                FAKE_COMPLETE = True
                STOP_PROGRESS_BAR = True
                thread.join()
                continue
                
            
            if r.status_code != 200:
                if r.status_code not in (500,404):
                    FAKE_COMPLETE = True
                STOP_PROGRESS_BAR = True
                thread.join()
                fprint('error',f'invalid mirror, got status code {r.status_code}')
                continue
            else:
                FAKE_COMPLETE = True
                STOP_PROGRESS_BAR = True
                thread.join()
            
            with open(filename, 'wb') as file:
                for data in r.iter_content(data_size): #64kiB
                    file.write(data)
            break
        else:
            fprint('error','all mirrors are invalid (press CTRL+C to stop program)')
            return None
        
        add_metadata(filename,theme_data["metadata"],Opts.Download.coverart)
        return filename
    else:
        return ''

def download_multi_theme(download_data,webm_folder=None,mp3_folder=None):
    """
    downloads multiple themes with download data
    """
    if webm_folder is None and mp3_folder is None:
        fprint('error','no save folder set')
    if webm_folder and not os.path.isdir(webm_folder):
        os.mkdir(webm_folder)
    if mp3_folder and not os.path.isdir(mp3_folder):
        os.mkdir(mp3_folder)
    
    download_chooser = (lambda mthd: 
        download_theme_audio_server(
            theme,mp3_folder,
            Opts.Download.no_redownload)
        if mthd == 0 else
        download_theme(
            theme,webm_folder,mp3_folder,
            Opts.Download.no_redownload)
    )
    
    # 0: external, 1: local
    if webm_folder is not None:
        mthd1,mthd2 = 1,1
    elif Opts.Download.local_convert:
        mthd1 = 1
        mthd2 = int(not Opts.Download.try_both)
    else:
        mthd1 = 0
        mthd2 = int(Opts.Download.try_both)
    
    if mthd1 == 0:
        fprint('progress','started downloading audio files')
    else:
        fprint('progress','started downloading'+(' and converting' if mp3_folder is not None else ''))
        
    for theme in download_data:
        filename = None
        allow_repeat = True
        while filename is None and allow_repeat:
            filename = download_chooser(mthd1)
            if filename is None:
                filename = download_chooser(mthd2)
            allow_repeat = Opts.Download.retry_forever          

def batch_download(
    username,
    statuses=[1,2],
    webm_folder=None,mp3_folder=None,
    anilist=False,
    extra_ids=[]
):
    """
    basically the main function
    given a username and destination, downloads all themes from MAL/AniList
    """
    fprint('progress','initializing program')
    download_data = get_download_data(username,statuses,anilist,extra_ids)
    download_multi_theme(download_data,webm_folder,mp3_folder)
    fprint('progress','finished downloading')


if __name__ == "__main__":
    pass
    
