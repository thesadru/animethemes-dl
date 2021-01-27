import logging
import sys

atdl_logger = logging.getLogger('animethemes-dl')
atdl_logger.setLevel(logging.ERROR)
logger = logging.getLogger('animethemes-dl.test')
logger.setLevel(logging.DEBUG if len(sys.argv)==2 else logging.INFO)

from . import (
    fetching,
    filters
)