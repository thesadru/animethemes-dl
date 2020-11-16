# animethemes-dl
![GitHub](https://img.shields.io/github/license/thesadru/animethemes-dl)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/thesadru/animethemes-dl)
![GitHub last commit](https://img.shields.io/github/last-commit/thesadru/animethemes-dl)
![GitHub Release](https://img.shields.io/github/v/release/thesadru/animethemes-dl?include_prereleases)

# what's this project
This project allows you to automaticaly download opening and ending songs from all of your favorite anime without the need of downloading everything yourself. Since almost every weeb uses MAL to track the anime he's watching, this tool is really useful, as every information you need to give it has been written down already. All you need to do is to enter your [MAL](https://myanimelist.net) or [AniList](https://anilist.co) username.

# disclaimer
All videos are downloaded from [animethemes.moe](https://animethemes.moe/). If you plan on using this program just for looking at openings, I recommend using [themes.moe](https://themes.moe/) instead. This program is made for creating your own playlist and such.

# what's this project for
This project was made for batch downloading themes from anime you have watched, but is programmed so it's easily improved, making it possible to add very easily. It's made with both command line usage and with python as a module.

# how to install
- clone this repository from [github.com](https://github.com/thesadru/animethemes-dl) or download it from pip with `pip install animethemes-dl`
- if you cloned, do `pip install -r requirements.txt` to install all required modules
- install ffmpeg into the same folder or in PATH

# usage in command line
make sure you have ffmpeg and python installed
possible commands: `animethemes-dl.bat` in windows, `animethemes-dl.sh` in linux. `animethemes-dl` if installed with pip. `python -m animethemes-dl` with python.
> All of these commands will be reffered to as `animethemes-dl` in the documentation.

## command line documentation
The script should raise errors in case you pass in an improper arg, but sometimes an error won't be raised if the error is not obvious, therefore make sure you read the documentation before running it.

You must set a username and a save folder.

### animelist
You must set a username. By default usernames are assumed to be a MAL user, you can use anilist instead with `--anilist`.

`--animelist-args` can be:
- url args for MAL ``
- `query` and `variables` for POST request for AniList
> `--animelist-args` are passed as a `<key>:<value>` pairs, for example: `sort1=1,sort2=14`

### animelist filters
There are filters for minimum score and priority.

`--minscore` is the minimum score between 0 and 10.
`--minpriority` is the minimum priority. For mal, use `Low=0,Medium=1,High=2`

### tag filters
You can filter out spoilers (with `--no-spoilers`) and nsfw (with `--no-nsfw`).
You can force tags with `--required-tags`, the possible tags are:
| Tag       | Meaning                                    | True Tag |
| :-------: | :----------------------------------------- | -------- |
| nocredits | No captions/no credits                     | NC       |
| lyrics    | Video includes English lyrics as subtitles | Lyrics   |
| bluray    | Video is sourced from a Blu-ray disc       | BD       |
| DVD       | Video is sourced from a DVD                | DVD      |
| 1080      | 1080p                                      | 1080     |
| 480       | 480p                                       | 480      |


### download
Downloads are by default disabled for both video and audio.
You can enable it by setting a save folder. Save folders are set with `-a` (audio) and `-v` (video).

The filename format can be changed with `--filename`.

The possible formats are defined in this table:
| Format            | Meaning                                       |
| ----------------- | :-------------------------------------------- |
| malid             | The MyAnimeList anime id.                     |
| status            | The watch status of the anime.                |
| year              | The year the anime was released.              |
| season            | The season the a nime was released.           |
| score             | Score of the anime.                           |
| priority          | Watch priority of the anime.                  |
| episodes          | Amount of episodoes in the anime.             |
| anime_title       | Title of the anime.                           |
| title             | Title of the song.                            |
| type              | Type of the anime theme.                      |
| shortype          | Type of the anime without index.              |
| version           | Version of the themes, set by animethemes.    |
| short_anime_title | Title of the anime made for use in filenames. |
| original_filename | Original filename of the video file.          |
| filetype          | Filetype of the theme. webm or mp3            |
> formats should be used as a python format string, meaning that it will be put as `%(format)s`.
For example `%(short_anime_title)s-%(type)s.%(filetype)s`

> Windows and Linux banned characters will be removed by default, to remove those and also unicode characters use `--ascii`

You can disable redownloading with `-r`. This is highly recommended.

The order of downloading can be set with `--sort`. This sorts the download data.

The possible sorts are defined in this table:
| Sort string | Meaning                           |
| ----------- | --------------------------------- |
| malid       | The MyAnimeList animeid.          |
| title       | Title of the anime.               |
| status      | The watch status of the anime.    |
| score       | Score of the anime.               |
| priority    | Watch priority of the anime.      |
| notes       | Your notes of the anime           |
| episodes    | Amount of episodoes in the anime. |
| year        | The year the anime was released.  |

You can add a coverart to audio files with `--coverart`, `--coverart` takes in a resolution, if set, image will be fetched from anilist.co, with high resolutions it's recommended to save them in `--coverart-folder`.

Downloader timeout can be changed with `--timeout` and max amount of retries with `--retries`.

### statuses
You can download anime that you have `--on-hold`,`--dropped` or `--planned`.

### compression
Downloaded files can be compressed in case you want to save them.

It will be enabled by setting a directory you want to compress with `--compress-dir`, this should be the same directory as you chosen one. The destination file is set with `--compress-name`, set it without the extension.
You can choose the `--compress-format`, this must be a format allowed by `shutils.make_archive`.

Additionally you can set the `--compress-base`.

### printing
You can set the loglevel with `--loglevel`. This will set the `logging.setLevel(x*10)`.
There are quick commands `--quiet` (print none) and `--verbose` (print all). To restrict download and ffmpeg messages, you MUST use `--quiet`.

You can disable color with `--no-color`.

### utilities
In case you haven't added ffmpeg to path, you can set the path with `--ffmpeg`.

You can `--repair` in case the script made some errors or you picked wrong options. This will delete unexpected files and readd metadata.

### settings
You can load options from a file with `--options`, the file is in json format.

The default options are:
```json
{
    "animelist": {
        "username": "",
        "anilist": false,
        "animelist_args": {},
        "minpriority": 0,
        "minscore": 0
    },
    "filter": {
        "spoilers": true,
        "nsfw": true,
        "nocredits": false,
        "lyrics": false,
        "bluray": false,
        "DVD": false,
        "1080": false,
        "480": false
    },
    "download": {
        "filename": "%(short_anime_title)s-%(type)s.%(filetype)s",
        "audio_folder": null,
        "video_folder": null,
        "no_redownload": false,
        "ascii": false,
        "timeout": 5,
        "retries": 3,
        "sort": null,
        "coverart": {
            "resolution": 0,
            "folder": null
        },
        "compression": {
            "root_dir": null,
            "base_name": "animethemes",
            "format": "tar",
            "base_dir": null
        }
    },
    "statuses": [1,2],
    "quiet": false,
    "no_colors": false,
    "ffmpeg": "ffmpeg",
    "ignore_prompts": false
}
```
> You can generate the options with `python -m animethemes_dl.models.options`.

## code documentation
The code uses the module `models` that contains models of `typing.TypedDict`.
Meaning python 3.8 is required.
Module `parsers` contains all parsers for MAL, Anilist and themes.moe.
Module tools contains extra tools for `animethemes-dl`.

examples:
```py
# parsers module uses API's to get data
import animethemes_dl.parsers as parsers
parsers.get_themes(username) # gets raw data
parsers.get_download_data(username) # gets download data

# models module uses typedDict to help language servers
import animethemes_dl.models as models
animelist: RawAnimeList = _myanimefunc()
metadata: Metadata = _mymetadatafunc2()

# tools have multiple tools used for several stuff
import animethemes_dl.tools as tools
tools.ffmpeg_covert(webm_file,mp3_file) # converts a webm file
tools.COLORS['progress'] = Fore.CYAN # changes colors
tools.compress_files(base,'zip',root) # compresses a direcotory
tools.update_metadata(
  parsers.get_download_data(username),False
) # updates metadata of all audio files

# you can implement your own batch dl
import animethemes_dl
data = parsers.get_download_data(username)
for theme in data:
  animethemes_dl.download_themes(theme,True)

# you can directly change options
animethemes_dl.setOptions(options)

# you can make special catchers
import animethemes_dl.errors as errors
try:
  animethemes_dl.batch_download(data)
except FfmpegException:
  print('I have no idea what happened')
```

# how does it work?
- parser
  - get data from MAL/AniList
  - get data from themes.moe
  - combine data
  - filter out unwanted themes
  - create download data
- download
  - download video file
  - convert video to audio
    - convert with ffmpeg
    - add mp3 metadata
- optional
  - compress files

# TODO
- code optimizations
- improve code documentation
- add track, artist and description metadata
