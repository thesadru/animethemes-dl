"""
utilities for animethemes_dl.parsers
"""
import time
from typing import Any
from urllib.parse import quote


def add_url_kwargs(url: str, kwargs: dict[str,Any]) -> str:
    """
    Adds url kwargs to the end of the url.
    """
    if not kwargs:
        return url
    return url+'?'+'&'.join(k+'='+quote(str(v)) for k,v in kwargs.items())

def remove_bracket(string: str):
    """
    removes brackets and stuff in them from strings
    """
    return string.replace('[','(').split('(')[0].strip()

def simplify_title(title: str):
    """
    Takes in an anime title and returns a simple version.
    """
    return ''.join(
        i for i in title if i.isalpha() or i==' '
    ).lower().strip()

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
