import json
import logging
import sys

from . import get_download_data, get_animethemes

if len(sys.argv) < 2:
    raise Exception('Must have a username, use like this: `parsers [dl|get] <username> <anilist>`')

logger = logging.getLogger('animethemes-dl')
logger.setLevel(logging.DEBUG)

if sys.argv[1] == 'get':
    data = get_animethemes(sys.argv[2],len(sys.argv)>3)
elif sys.argv[1] == 'dl':
    data = get_download_data(sys.argv[2],len(sys.argv)>3)
else:
    quit('improper category')

path = 'animethemes_test.json'
with open(path,'w') as file:
    json.dump(data,file,indent=4)

logger.info(f'Saved data to {path}.')
