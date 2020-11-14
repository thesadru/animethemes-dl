"""
utilities for animethemes_dl.parsers
"""
import time


def add_url_kwargs(url,kwargs={}):
    if not kwargs:
        return url
    kwargs = '&'.join(f'{k}={v}' for k,v in kwargs.items())
    return url+'?'+kwargs

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
