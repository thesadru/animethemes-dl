"""
utilities for animethemes_dl.parsers
"""
def add_url_kwargs(url,kwargs={}):
    if not kwargs:
        return url
    kwargs = '&'.join(f'{k}={v}' for k,v in kwargs.items())
    return url+'?'+kwargs
