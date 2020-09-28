import sys
from globals import Opts
from colorama import init,Style,Fore
init()


def color_category(category):
    if Opts.Print.no_color:
        return '['+category+']'
    
    color = {
        'progress':Fore.GREEN,
        'get':Fore.YELLOW,
        'download':Fore.CYAN,
        'convert':Fore.CYAN,
        'parse':Fore.LIGHTYELLOW_EX,
        'error':Fore.RED
    }[category]
    return '['+color+category+Style.RESET_ALL+']'

def fprint(category,message=None,end='\n'):
    if Opts.Print.quiet:
        return
    if message is None:
        sys.stdout.write(str(category)+'\n')
    else:
        message = color_category(category)+' '+str(message)+end
        sys.stdout.write(message)
