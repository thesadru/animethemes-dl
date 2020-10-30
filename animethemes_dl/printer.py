"""
animethemes-dl custom print
allows the use of quiet and no-color
"""
import sys
from .globals import Opts
from colorama import init,Style,Fore
init()


def color_category(category):
    """
    adds color to a category and puts it in brackets
    """
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

def fprint(category,message='',start='',end='\n'):
    """
    animethemes-dl custom print function
    colors a given category and then it puts it in brackets
    if no message is given, the category will be printed like a normal `print`
    """
    if Opts.Print.quiet:
        return
    if message:
        message = start+color_category(category)+' '+str(message)+end
        sys.stdout.write(message)
    else:
        sys.stdout.write(start+str(category)+end)
