#!/usr/bin/env python
from downloader import to_mal_priority,batch_download
from printer import fprint
from globals import Opts
from os.path import realpath
import argparse
import sys
import json


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
    default='',
    nargs='?',
    help="Your animelist username")
parser.add_argument('--anilist','--al',
    action="store_true",
    help="Use Anilist instead of MyAnimeList")
parser.add_argument('-s','--settings',
    default=None,
    type=realpath,
    help="A settings file in json format. Check out README.md for more info.")
parser.add_argument('-id','--id','--mal-ids',
    type=int,
    nargs='+',
    help="mal id's of anime that should be also downloaded.")

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
download.add_argument('-d','--no-dialogue','--no-trans',
    action='store_true',
    help="Does not download themes that have dialogue in them.")
download.add_argument('--sfw','--no-nsfw',
    action='store_true',
    help="Does not download themes that are nsfw")
download.add_argument('--no-spoilers',
    action='store_true',
    help="Does not download themes that have spoilers in them.")
download.add_argument('-f','--filename',
    default='',
    help="how the filename should be generated, reffer to the README for exact instructions")
download.add_argument('--retry-forever',
    action='store_true',
    help="Will forever retry downloading mirrors. (unreliable)")
download.add_argument('--ascii',
    action='store_true',
    help="no special characters will be in the filename, only ascii chars")
download.add_argument('--coverart','--add-coverart',
    action='store_true',
    help="Adds coverart to mp3 files")
download.add_argument('--ffmpeg','--ffmpeg-path',
    default='ffmpeg',
    help="Your ffmpeg path if it's not installed in PATH")
download.add_argument('--local-convert',
    action='store_true',
    help="Converts files locally, instead of converting them on the server, good for a supercomputer.")
download.add_argument('--try-both','--try-both-download-methods',
    action='store_true',
    help="if a download method fails, tries the other one.")
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
printer.add_argument('--print-settings',
    action="store_true",
    help="Prints settings when the script starts.")

args = parser.parse_args()

args.status = args.status or []
args.status = [1,2]+args.status
args.id = args.id or []

if args.settings is not None:
    with open(args.settings) as file:
        jargs = json.load(file)
        if 'quiet' not in jargs:
            jargs['quiet'] = False
        for k in jargs:
            args.__setattr__(k,jargs[k])

Opts.update(**args.__dict__)

args.status.append(0)

if args.print_settings: 
    fprint('\n'.join([f'{k}={repr(v)}' for k,v in Opts.get_settings().items()]),end='\n\n')

if args.username == '' and len(args.id) == 0:
    fprint('error','no username set')
    quit()

if args.video is None and args.audio is None:
    fprint('error','no save folder set')
    quit()

batch_download(
    args.username,
    args.status,
    args.video,args.audio,
    args.anilist,
    args.id
)
