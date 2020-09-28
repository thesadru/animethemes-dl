from downloader import to_mal_priority,batch_download
from printer import fprint
from globals import Opts
from os.path import realpath
import argparse
import sys


__doc__ = """
Batch downloads themes from every anime you have watched with themes.moe.
Supports multiple filters, adding metadata and smart file naming.

requirements:
You must have ffmpeg installed in the same folder or on PATH.
"""

parser = argparse.ArgumentParser(
    description=__doc__,
    epilog="Check the README.md if there are problems.",
    prog='animethemes-dl'
)

parser.add_argument('username',
    help="Your animelist username")
parser.add_argument('--anilist','--al',
    action="store_true",
    help="Use Anilist instead of MyAnimeList")

animelist = parser.add_argument_group('animelist filters')
animelist.add_argument('--minscore',
    type=int,
    default=0,
    choices=range(11),
    help="Minimum score that an anime must have to be downloaded (uses 1-10 scale)")
animelist.add_argument('--minpriority',
    type=to_mal_priority,
    default=0,
    choices=[0,1,2,'Low','Medium','High'],
    help="Minimum priority that an anime must have to be downloaded")

statuses = parser.add_argument_group('status filters')
statuses.add_argument('--on-hold',
    const=3,
    dest='status',
    action='append_const',
    help="Download anime that are on-hold")
statuses.add_argument('--dropped',
    const=4,
    dest='status',
    action='append_const',
    help="Download anime that are dropped")
statuses.add_argument('--planned',
    const=6,
    dest='status',
    action='append_const',
    help="Download anime that are planned")

folders = parser.add_argument_group('save folders',"If a folder is not set, files will not be downloaded")
folders.add_argument('-v','--video','--video-folder',
    type=realpath,
    default=None,
    help="video save folder")
folders.add_argument('-a','--audio','--audio-folder',
    type=realpath,
    default=None,
    help="audio save folder")
folders.add_argument('--audio-format',
    default='mp3',
    help="change the audio format (without a .), default is `mp3`")

download = parser.add_argument_group('download filters')
download.add_argument('-r','--no-redownload',
    action='store_true',
    help="Does not redownload themes that are already downloaded")
download.add_argument('-d','--no-dialogue','--no-spoiler',
    action='store_true',
    help="Does not download themes that have dialogue in them (unreliable!)")
download.add_argument('-s','--sfw','--no-nsfw',
    action='store_true',
    help="Does not download themes that are nsfw")
download.add_argument('-f','--filename',
    default='',
    help="how the filename should be generated, reffer to the README for exact instructions")
download.add_argument('--ascii',
    action='store_true',
    help="no special characters will be in the filename, only ascii chars")
download.add_argument('--metadata','--metadata-version',
    type=int,
    default=0,
    choices=[0,1,2],
    help="ID3 version (0 meaning both)")
download.add_argument('-p','--preffered',
	type=lambda x: x.lower(),
	default=[],
	nargs='+',
    help="Preffered tags for themes, look at the README for all avalible tags. Seperate tags by space, with the most wanted at the start.")

printer = parser.add_argument_group('print arguments')
printstyle = printer.add_mutually_exclusive_group()
printstyle.add_argument('-c','--no-color','--no-colored-print',
    action='store_true',
    help="Does not print in color")
printstyle.add_argument('-q','--quiet','--no-print',
    action='store_true',
    help="Does not print to console")

args = parser.parse_args()

args.status = args.status or []
args.status = [1,2]+args.status

Opts.update(**args.__dict__)
print(Opts.settings())

if args.video is None and args.audio is None:
    fprint('error','no save folder set')
    quit()

batch_download(
    args.username,
    args.status,
    args.video,args.audio,
    args.anilist
)