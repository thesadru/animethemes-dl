"""
global options
"""
import sys,json

class Opts:
    """
    The options class
    Uses a quirk of python to use easy global variables
    DO NOT INITIALIZE
    """
    class Animelist:
        @classmethod
        def update(cls,
            minscore=0,
            minpriority=0,
            **kwargs
        ):
            kwargs = locals().copy()
            for k,v in kwargs.items():
                if k not in {'cls','kwargs'}:
                    exec(f'cls.{k} = '+repr(v))
    class Download:
        @classmethod
        def update(cls,
            no_redownload=False,
            no_dialogue=False,
            sfw=False,
            no_spoilers=False,
            filename='',
            retry_forever=False,
            audio_format='mp3',
            ascii=False,
            coverart=False,
            ffmpeg='ffmpeg',
            local_convert=False,
            try_both=False,
            preffered=[],
            **kwargs
        ):
            kwargs = locals().copy()
            for k,v in kwargs.items():
                if k not in {'cls','kwargs'}:
                    exec(f'cls.{k} = '+repr(v))
    
    class Print:
        @classmethod
        def update(cls,
            no_color=False,
            quiet=True,
            print_settings=False,
            **kwargs
        ):
            kwargs = locals().copy()
            for k,v in kwargs.items():
                if k not in {'cls','kwargs'}:
                    exec(f'cls.{k} = '+repr(v))
    @classmethod
    def update(cls,**kwargs):
        cls.Animelist.update(**kwargs)
        cls.Download.update(**kwargs)
        cls.Print.update(**kwargs)
    
    @classmethod
    def get_settings(cls):
        out = {}
        for k,v in cls.__dict__.items():
            if k.startswith('_') or k == 'update':
                continue
            for k,v in v.__dict__.items():
                if k.startswith('_') or k == 'update':
                    continue
                out[k] = v
        return out
                    

Opts.update()


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'make_settings_file':
        with open(sys.argv[2],'w') as file:
            d = {'username':'','anilist':False,'audio':None,'video':None,'status':[1,2],'print_settings':False,'id':[]}
            d.update(Opts.get_settings())
            d['quiet'] = False
            json.dump(d,file,indent=4)
