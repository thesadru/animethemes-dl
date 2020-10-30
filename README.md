<div align="center">
  <h1>animethemes-dl</h1>
  Download anime themes with myanimelist.
  
  ![GitHub](https://img.shields.io/github/license/thesadru/animethemes-dl)
  ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/thesadru/animethemes-dl)
  ![GitHub last commit](https://img.shields.io/github/last-commit/thesadru/animethemes-dl)
  ![GitHub Release](https://img.shields.io/github/v/release/thesadru/animethemes-dl?include_prereleases)
</div>

# what's this project
This project allows you to automaticaly download opening and ending songs from all of your favorite anime without the need of downoading everything yourself. Since almost every weeb uses MAL to track the anime he's watching, this tool is really useful, as every information you need to give it has been written down already. All you need to do is to enter your [MAL](https://myanimelist.net) or [AniList](https://anilist.co) username.
# disclaimer
All videos are downloaded from [animethemes.moe](https://themes.moe/) and originally belong to studios who made them. You are not allowed to distribute any videos downloaded, unless you have permission from the studios that made it and animethemes.moe.
Note that owning and distributing the program itself is allowed.
# how to install
- clone this repository or download it from pip with `pip install animethemes-dl`
- if you cloned, do `pip install -r requirements.txt` to install all required libraries
- install ffmpeg into the same folder or in PATH
# usage
- make sure you have ffmpeg and python installed
- run `animethemes-dl.[bat|sh] -h ` for help
- run `animethemes-dl.[bat|sh] <username> <settings>` to download your songs
- if you have installed with pip, running `animthemes-dl` should work.
## guide
you may need to use `python main.py` instead of `animethemes-dl`

The most barebones download requires a username and a save folder.
Username refferes to your MAL username, alternatively if you want to use AniList, you need to use `--anilist`.
Save folders can be set by `-a` (audio) and `-v` (video).
```
animethemes-dl sadru -a "themes"
animethemes-dl sadru --anilist -v "anime oped"
```

Use `--settings` to get settings from a json file.
```
animethemes-dl --settings "settings.json"
```

If you want extra anime to be downloaded use `--id`.
Ids passed must be MAL's anime id.
```
animethemes-dl --id 42364 31240
```

Set the audio format with `--audio-format`. Works only if converting locally
```
animethemes-dl --audio-format wav
```

You can do some filtering based on your animelist. either by status or by score/priority.
All videos that you are currently watching and have completed are downloaded. You can add other statuses by using `--on-hold`, `--dropped` or `--planned`.
Set the minimum score (range 0-10) with `--minscore` and minimum priority (Low,Medium,High) with `--minpriority`.
```
animethemes-dl --minscore 7 --minpriority High
animethemes-dl --dropped
```

Currently you can filter out all NSFW themes with `--sfw` and all themes with dialogue in them with `--no-dialogue`.
There may be cases where there's no dialogue tag but it still has dialogue, that is because this theme happens to have important dialogue in them (complain to animethemes about this). If you don't want that use `--no-spoilers`.
```
animethemes-dl --sfw --no-dialogue --no-spoilers
```

When downloading, you can choose to not redownload songs that are already in the save folder with `-r`.
If your download keeps missing some themes, you can use `--retry-forever` to force the download, this is currently highly unreliable.
To fix problems with downloading you can use `--local-convert` which converts themes to audio with ffmpeg instead of having it converted and then downloaded. This is may be slow however, so you can use `--try-both` to try the chosen method, and then the other one.
```
animethemes-dl --local-convert --retry-forever
animethemes-dl --try-both
```

You can modify filenames by using `--filename` (look at filename naming for more info). If your system/player cannot read Japanese characters or emojis, use `--ascii` to remove them from the filename.
```
animethemes-dl --filename "%a-%t.%e" --ascii
```

Add coverart to mp3 files with `--coverart`. Uses ID3 COVER_ART (id 3) to do so. 
CURRENTLY DOESN'T WORK.
```
animethemes-dl --coverart
```

Set path to ffmpeg with `--ffmpeg`. Most bugs might come from ffmpeg not being 'trusted'. Try `./ffmpeg`.
```
animethemes-dl --ffmpeg "../../utilities/ffmpeg"
```

You can choose which tags you preffer by using `--preffered` (look at preffered tags for more info).
```
animethemes-dl --preffered Lyrics Cen 60FPS
```

You can turn off printing with `--quiet`, turn off color with `--no-color`.
Print all args with `--print-settings` for bugfixing.
```
animethemes-dl --quiet
animethemes-dl --no-color --print-settings
```

## usage examples
These are some of the settings I (may) personally use.
```
animethemes-dl sadru -a "anime themes"
animethemes-dl sadru -a "anime themes" --minscore 5 -r -d --try-both --ffmpeg "./ffmpeg" --coverart --filename "%a%t.%e"
animethemes-dl sadru -a "anime themes" --anilist --minpriority Medium -r --audio-format ogg --sfw
```

# filename naming
Filename are by the default named `%A %t (%S).%e` which returns for example: `AppareRanman OP (I got it!).webm`
variables are:
```
%% = percent symbol ("%")
%a = short anime name (no spaces)
%A = long anime name (spaced)
%t = theme type [OP | ED]
%s = song name (underscored)
%S = song name (spaced)
%e = extension [webm | mp3]
```
# preffered tags
You can value some tags over other by adding it to the preffered tags.
They are valued by asigning points to them, like this: `['NC','BD','720']` will be: `NC:3, BD:2, 720:1`.
By default more tags will be put higher.
avalible tags:

| Tag     | Meaning |
|:-------:|:--------|
| NC	    | No captions/no credits |
| Subbed  |	Video includes subtitles of dialogue |
| Lyrics  |	Video includes English lyrics as subtitles |
| Cen	    | Video is censored |
| Uncen	  | Video is uncensored from original broadcast |
| 60FPS	  | Video is 60 frames per second |
| Trans	  | Part of the anime episode transitions into the video |
| BD	    | Video is sourced from a Blu-ray disc |
| 420     | 420p |
| 720	    | 720p |
| 1080	  | 1080p |
# settings file
default settings look like:
```json
{
    "username": "",
    "anilist": false,
    "audio": null,
    "video": null,
    "status": [1,2],
    "print_settings": false,
    "id":[],
    "minscore": 0,
    "minpriority": 0,
    "no_redownload": false,
    "no_dialogue": false,
    "sfw": false,
    "filename": "",
    "retry_forever": false,
    "audio_format": "mp3",
    "ascii": false,
    "coverart": false,
    "ffmpeg": "ffmpeg",
    "local_convert": false,
    "try_both": false,
    "preffered": [],
    "no_color": false,
    "quiet": true
}
```
# how does it work?
This code grabs your animelist data, filters it based off your settings, puts it through an api and then downloads it
- get your anime data
  - pull data from MAL/AniList
  - pull data from animethemes
  - sort them based on status and mirrors
- download
  - filter out spoilers/NSFW
  - download song (and convert)
# TODO
- code optimizations
- add track, artist and description metadata
- add progress to download
- add an option to delete files that would have been filtered out