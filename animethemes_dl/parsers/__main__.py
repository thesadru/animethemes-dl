import json
import sys
from pprint import pprint
from .parser import get_animethemes

with open('animethemes_test.json','w') as file:
    data = get_animethemes(sys.argv[1],len(sys.argv)>2)
    print('got data!',sum(len(i) for i in data.values()))
    json.dump(data,file,indent=4)
