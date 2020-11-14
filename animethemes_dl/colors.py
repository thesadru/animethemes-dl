"""
For pretty logging
"""
import logging
from colorama import init, Fore
from .options import OPTIONS
init()

# there are 8 colors, 6 of which are used (no white/black)
COLORS = {
    'progress':Fore.GREEN,
    'get':Fore.YELLOW,
    'download':Fore.CYAN,
    'error':Fore.RED,
    
    'parse':Fore.BLUE,
    'convert':Fore.MAGENTA
}

def color_category(cat: str) -> str:
    """
    Colors a category
    """
    return '['+COLORS.get(cat,'')+cat+Fore.RESET+']'

def color_message(msg: str) -> str:
    """
    Colors a message
    """
    category = msg.split()[0][1:-1]
    if OPTIONS['no_colors'] or category not in COLORS:
        return msg

    return color_category(category) + msg[len(category)+2:]

class ColorFormatter(logging.Formatter):
    """
    A custom logging factory.
    Takes out a keyword and replaces it with a colored one
    """
    def format(self,record):
        record.msg = color_message(record.msg)
        return super().format(record)
