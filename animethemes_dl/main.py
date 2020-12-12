"""
Command line version of animethemes-dl.
"""
import argparse
import json
import logging
from os.path import realpath
from pprint import pformat

from animethemes_dl.parsers.dldata import get_download_data

from .downloader import batch_download
from .options import OPTIONS, _update_dict
from .tools import repair

logger = logging.getLogger('animethemes-dl')

__doc__ = """\
Batch downloads themes from every anime you have watched with themes.moe.
Supports multiple filters, adding metadata and smart file naming.

requirements:
You must have ffmpeg installed in the same folder or on PATH.\
"""

parser = argparse.ArgumentParser(
    description=__doc__,
    epilog="Remember to also check the README.md.",
    prog='animethemes-dl'
)
# =============================================================================
utils = parser.add_argument_group('utilities')
utils.add_argument(
    '--ffmpeg',
    metavar="PATH",
    type=realpath,
    help="path to ffmpeg, in case it's not in PATH"
)
utils.add_argument(
    '-s','--settings','--options',
    type=realpath,
    help="The settings file in json format. Uses the Options model."
)
utils.add_argument(
    '--repair',
    action='store_true',
    help="Deletes unexpected files, readds metadata"
)

# =============================================================================
animelist = parser.add_argument_group('animelist')
animelist.add_argument(
    'username',
    default=None,
    nargs='?',
    help="Your animelist username."
)
animelist.add_argument(
    '--anilist','--al',
    action='store_true',
    help="Use Anilist instead of MyAnimeList"
)

animelist.add_argument(
    '--animelist-args',
    type=lambda x:dict(i.split('=') for i in x.split(',')),
    default={},
    metavar="KWARGS",
    help="Animelist arguments, url args for MAL"
)

animelist_filters = parser.add_argument_group('animelist filters')
animelist_filters.add_argument(
    '--minscore',
    type=int,
    default=0,
    metavar="INT[0-10]",
    help="Minimum score that an anime must have to be downloaded (0-10 scale)"
)
animelist_filters.add_argument(
    '--minpriority',
    type=int,
    default=0,
    metavar="INT[0-2]",
    help="Minimum priority that an anime must have to be downloaded (0-2 scale)"
)
animelist_filters.add_argument(
    '--range',
    type=int,
    default=[0,0],
    nargs=2,
    metavar="INT",
    help="Uses only a set range of an animelist."
)

tag_filters = parser.add_argument_group('tag filters')
tag_filters.add_argument(
    '--smart','--smart-filter',
    action='store_true',
    help="Smart filters out dialogue."
)
tag_filters.add_argument(
    '--required-tags','--rtags',
    default=[],
    metavar="TAGS",
    nargs='+',
    help="Required tags for themes, check README for possible tags."
)
tag_filters.add_argument(
    '--banned-tags','--btags',
    default=[],
    metavar="TAGS",
    nargs='+',
    help="Banned tags for themes, check README for possible tags."
)
tag_filters.add_argument(
    '--min-resolution','--res',
    default=0,
    type=int,
    metavar="INT",
    help="Minimum resolution of video."
)
tag_filters.add_argument(
    '--source',
    default=None,
    choices=('','DVD','BD'),
    metavar="TAG",
    help="The required source. Either DVD or BD."
)
tag_filters.add_argument(
    '--overlap','--over',
    default=None,
    nargs='+',
    choices=('Over','Transition','None'),
    metavar="TAG",
    help="Give only themes with given overlap. Either Over,Transition or None."
)


# =============================================================================
download = parser.add_argument_group('download')
download.add_argument(
    '-a','--audio','--audio-folder',
    type=realpath,
    metavar="PATH",
    help="Audio save folder."
)
download.add_argument(
    '-v','--video','--video-folder',
    type=realpath,
    metavar="PATH",
    help="Video save folder."
)
download.add_argument(
    '--filename','--filename-format',
    metavar="FORMAT",
    help="A format string for filenames, check README for possible args."
)
download.add_argument(
    '-r','--no-redownload',
    action='store_true',
    help="Does not redownload themes that are already downloaded."
)
download.add_argument(
    '-u','--update',
    action='store_true',
    help="Updates files. Will not skip redownload if the file size is different.\
          Must have stored video somewhere"
)
download.add_argument(
    '--ascii',
    action='store_true',
    help="Strips all unicode characters from filenames."
)
download.add_argument(
    '--coverart',
    type=int,
    default=0,
    const=1,
    choices=[0,1,2],
    nargs='?',
    metavar="INT[1,2]",
    help="Adds coverart to audio files. You can add a resolution in range 1-3."
)
download.add_argument(
    '--coverart-folder',
    metavar="PATH",
    help="Saves all coverarts to a folder."
)
download.add_argument(
    '--timeout',
    type=int,
    default=5,
    metavar="INT",
    help="Timeouts after x seconds."
)
download.add_argument(
    '--retries','--max-retries',
    type=int,
    default=3,
    metavar="INT",
    help="Max retries"
)
download.add_argument(
    '--force-videos','--fvideos',
    default=[],
    type=int,
    nargs='+',
    help="Force video ids to be downloaded. It will not be included in filters."
)
download.add_argument(
    '--max-animethemes-age',
    default=2*24*60*60*60,
    type=int,
    help="How long a requests file can be. Used to optimize getting data, since it's rate limited."
)
# =============================================================================
statuses = parser.add_argument_group('statuses')
statuses.set_defaults(statuses=[1,2])
statuses.add_argument(
    '--on-hold',
    const=3,
    dest='statuses',
    action='append_const',
    help="Download anime that are on-hold."
)
statuses.add_argument(
    '--dropped',
    const=4,
    dest='statuses',
    action='append_const',
    help="Download anime that are dropped."
)
statuses.add_argument(
    '--planned',
    const=6,
    dest='statuses',
    action='append_const',
    help="Download anime that are planned."
)

# =============================================================================
compression = parser.add_argument_group('compression')
compression.add_argument(
    '--compress-dir',
    default=None,
    metavar="PATH",
    help="If set, the directory name to compress, should just be the save folder"
)
compression.add_argument(
    '--compress-name',
    default='animethemes',
    metavar="PATH",
    help="Where to save the the compressed files. Without the extension."
)
compression.add_argument(
    '--compress-format',
    default='tar',
    metavar="COMPRESS_FORMAT",
    help="Compression format, the extension after compress-name. Check README for possible formats."
)
compression.add_argument(
    '--compress-base',
    default=None,
    metavar="LOCAL_PATH",
    help="The base dir of compression."
)

# =============================================================================
printing = parser.add_argument_group('printing')
printing.set_defaults(loglevel=2)
printing.add_argument(
    '-q','--quiet',
    const=6,
    dest='loglevel',
    action='store_const',
    help="Does not print anything, basically `--loglevel 6`."
)
printing.add_argument(
    '--verbose',
    const=1,
    dest='loglevel',
    action='store_const',
    help="Prints verbose, basically `--loglevel 1`."
)
printing.add_argument(
    '--loglevel',
    type=int,
    choices=range(1,6),
    metavar="INT[1-6]",
    dest='loglevel',
    action='store',
    help="Sets the loglevel, 2 by default. Uses logging as the loglevel, \
          meaning lower the level, the more information there will be."
)
printing.add_argument(
    '--no-color',
    action='store_true',
    help="Does not print in color."
)

def get_filters(args):
    tags = ('spoiler','nsfw','nc','subbed','lyrics','uncen')
    filters = {}
    for f in tags:
        r,b = f in args.required_tags,f in args.banned_tags
        if r==b:
            filters[f] = None
        elif r:
            filters[f] = True
        elif b:
            filters[f] = False
    
    return filters

def load_settings(settings):
    if settings is None:
        return {}
    with open(settings,'r') as file:
        return json.load(file)

def parse_args(args):
    filters = get_filters(args)
    options = _update_dict(OPTIONS,
    {
        "animelist": {
            "username": args.username,
            "anilist": args.anilist,
            "animelist_args": args.animelist_args,
            "minpriority": args.minpriority,
            "minscore": args.minscore
        },
        "filter": {
            'spoiler': filters['spoiler'],
            'nsfw': filters['nsfw'],
            'resolution': args.min_resolution,
            'nc': filters['nc'],
            'subbed': filters['subbed'],
            'lyrics': filters['lyrics'],
            'uncen': filters['uncen'],
            'source': args.source,
            'overlap': args.overlap,
        },
        "download": {
            **({"filename": args.filename} if args.filename else {}),
            "audio_folder": args.audio,
            "video_folder": args.video,
            "no_redownload": args.no_redownload,
            "update": args.update,
            "ascii": args.ascii,
            "timeout": args.timeout,
            "retries": args.retries,
            "max_animethemes_age": args.max_animethemes_age,
            "force_videos": args.force_videos
        },
        "coverart": {
            "resolution":args.coverart,
            "folder":args.coverart_folder
        },
        "compression": {
            "root_dir":args.compress_dir,
            "base_name":args.compress_name,
            "format":args.compress_format,
            "base_dir":args.compress_base
        },
        "statuses": args.statuses,
        "quiet": args.loglevel>logging.CRITICAL,
        "no_colors": args.no_color,
        "ffmpeg": args.ffmpeg
    })
    return _update_dict(options,load_settings(args.settings))

def check_errors(options):
    errors = []
    if not options['animelist']['username']:
        errors.append('No username set.')
    elif not options['animelist']['username'].strip():
        errors.append('Improper username')
    if not options['download']['audio_folder'] and not options['download']['video_folder']:
        errors.append('No audio or video save folder.')
    if 'filename' in options['download'] and not options['download']['filename'].count('%'):
        errors.append('No format in filename, will have overwrites.')
    return errors

def raise_for_errors(options):
    errors = check_errors(options)
    for i in errors:
        logger.exception('message')
    if errors:
        raise ValueError(*errors)

def main():
    args = parser.parse_args()
    options = parse_args(args)
    
    logger.setLevel(args.loglevel*10)
    logger.debug(pformat(options))
    
    raise_for_errors(options)
    
    if args.repair:
        repair(get_download_data(
            OPTIONS['animelist']['username'],
            OPTIONS['animelist']['anilist'],
            OPTIONS['animelist']['animelist_args']
        ))
    else:
        batch_download(options)

if __name__ == "__main__":
    main()
