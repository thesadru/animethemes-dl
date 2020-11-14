import logging

from ..errors import BadThemesUrl
from ..models import ADownloadData
from ..colors import ColorFormatter

logger = logging.getLogger('animethemes-dl')

def fix_faulty_url(data: ADownloadData):
    """
    Removes the tags ("...-OP1-NCBD.webm" -> "...,OP1,NCBD.webm" -> "...-OP1.webm")
    Used when themes.moe returns a stupid url.
    """
    if data['url'].count('-') == 1:
        raise BadThemesUrl(f'Cannot get a good url for {data["url"]}')
    else:
        url = '-'.join(data['url'].split('-')[:2])+'.webm'
        logger.debug(f'Url "{data["url"]}" failed, trying "{url}"')
        return url

def init_logger():
    """
    Initializes the animethemes_dl logger.
    """
    logger = logging.getLogger('animethemes-dl')
    if logger.handlers:
        return False
    
    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    
    logger_handler.setFormatter(ColorFormatter())
    
    logger.propagate = False

    return True