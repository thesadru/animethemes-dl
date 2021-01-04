"""
utilities for animethemes_dl.parsers
"""
import re
import time
from typing import Any


def add_url_kwargs(url: str, kwargs: dict[str,Any]={}) -> str:
    """
    Adds url kwargs to the end of the url.
    """
    if not kwargs:
        return url
    kwargs = '&'.join(f'{k}={v}' for k,v in kwargs.items())
    return url+'?'+kwargs

def remove_bracket(string: str):
    """
    removes brackets and stuff in them from strings
    """
    return string.replace('[','(').split('(')[0]

def simplify_title(title: str):
    """
    Takes in an anime title and returns a simple version.
    """
    return ''.join(
        i for i in title if i.isalpha() or i==' '
    ).lower().strip()

def add_honorific_dashes(string: str):
    """
    Adds dashes "-" in front of honorifics.
    """
    return re.sub(r'[^-](san|chan|kun|sama|tan)',r'-\1',string)

class Measure:
    """
    Measures how long it was between intitalization and calling
    """
    def __init__(self):
        self.time = time.time()
    def get(self,ndigits=2):
        return round(time.time()-self.time,ndigits)
    def __call__(self,ndigits=2):
        return self.get(ndigits)
