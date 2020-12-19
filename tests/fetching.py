import logging

from animethemes_dl.options import OPTIONS
from animethemes_dl.parsers import get_mal, get_anilist, fetch_animethemes

logger = logging.getLogger('animethemes-dl.test')

mal = get_mal('sadru')
logger.info(f"Got {len(mal)} entries from MAL.")
logger.info(f"Got {len(get_anilist('sadru'))} entries from AniList.")
logger.info(f"Got {len(fetch_animethemes(mal))} entries from AnimeThemes (root MAL).")
