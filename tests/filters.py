import logging

from animethemes_dl.options import OPTIONS
from animethemes_dl.parsers.animethemes import fetch_animethemes
from animethemes_dl.parsers.dldata import parse_download_data
from animethemes_dl.parsers.myanimelist import get_mal

logger = logging.getLogger('animethemes-dl.test')

raw = fetch_animethemes(get_mal('sadru'))
for f in ('spoiler','nsfw', 'nc', 'subbed', 'lyrics', 'uncen'):
    none = len(parse_download_data(raw))
    for x in (True,False):
        OPTIONS['filter'][f] = x
        modified = len(parse_download_data(raw))
        logger.debug(f'Filter {f}:{int(x)} gives {modified}x{none}.')
        if modified==none:
            logger.error(f'Filter "{f}" does nothing when "{x}".')
    
    OPTIONS['filter'][f] = None
