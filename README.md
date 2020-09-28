<div align="center">
  
  Download anime themes with myanimelist.
  
  ![GitHub](https://img.shields.io/github/license/thesadru/animethemes-dl)
  ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/thesadru/animethemes-dl)
  ![GitHub last commit](https://img.shields.io/github/last-commit/thesadru/animethemes-dl)
  ![GitHub Release](https://img.shields.io/github/release/thesadru/animethemes-dl)
</div>

# what's this project
This project allows you to automaticaly download opening and ending songs from all of your favorite anime without the need of downoading everything yourself. Since almost every weeb uses MAL to track the anime he's watching, this tool is really useful, as every information you need to give it has been written down already. All you need to do is to enter your [MAL](https://myanimelist.net) or [AniList](https://anilist.co) username.
# disclaimer
All videos are downloaded from [animethemes.moe](https://themes.moe/) and originally belong to studios who made them. You are not allowed to distribute any videos downloaded, unless you have permission from the studios that made it and animethemes.moe.
Note that owning and distributing the program itself is allowed.
# how to install
- clone this repository or download it
- do `pip install -r requirements.txt` to install all required libraries
- install ffmpeg into the same folder or in PATH
# usage
- make sure you have ffmpeg and python installed
- run `python main.py -h` for help
- run `python main.py <username> <settings>` to download your songs
# filename naming
Filename are by the default named `%a %t (%S).%e` which returns for example: `AppareRanman OP (I got it!).webm`
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
# how does it work?
This code grabs your animelist data, filters it based off your settings, puts it through an api and then downloads it
- get your anime data
  - pull data from MAL
  - filter data
- get theme data
  - filter out spoilers/NSFW
  - download song
  - convert to mp3 with ffmpeg
# TODO
- code optimizations
- network optimizations
- higher usability with importing
- download only one song
- settings grabbed from a file
- set up preffered
