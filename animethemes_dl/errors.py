"""
Custom animethemes-dl exceptions and errors.
"""

class AnimeThemesDLException(Exception): pass

class AnimeListException(AnimeThemesDLException): pass
class AnilistException(AnimeListException): pass
class MyanimelistException(AnimeListException): pass
class AnimeThemesTimeout(AnimeThemesDLException): pass

class FfmpegException(AnimeThemesDLException): pass

class BadThemesUrl(AnimeThemesDLException): pass