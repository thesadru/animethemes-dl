import json
import sys
import logging
from ..options import OPTIONS,setOptions
from . import get_themes,get_download_data

if len(sys.argv) < 2:
    raise Exception('Must have a username, use like this: `parsers [dl|get] <username> <anilist>`')

logging.basicConfig(level=logging.DEBUG)

options = {
    'filter':{
        '1080':True,
        'spoilers':False
    }
}
setOptions(options)

if sys.argv[1] == 'get':
    data = get_themes(sys.argv[2],len(sys.argv)>3)
elif sys.argv[1] == 'dl':
    data = get_download_data(sys.argv[2],len(sys.argv)>3)
else:
    quit('improper category')

path = 'animethemes_test.json'
with open(path,'w') as file:
    json.dump(data,file,indent=4)

logging.info(f'Saved data to {path}.')
