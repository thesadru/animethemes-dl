import logging

from ..errors import BadThemesUrl
from ..models import ADownloadData


def fix_faulty_url(data: ADownloadData):
    """
    Removes the tags ("...-OP1-NCBD.webm" -> "...,OP1,NCBD.webm" -> "...-OP1.webm")
    Used when themes.moe returns a stupid url.
    """
    if data['url'].count('-') == 1:
        raise BadThemesUrl(f'Cannot get a good url for {data["url"]}')
    else:
        url = '-'.join(data['url'].split('-')[:2])+'.webm'
        logging.debug(f'Url "{data["url"]}" failed, trying "{url}"')
        return url
