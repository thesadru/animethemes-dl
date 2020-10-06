import sys

class Opts:
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
			filename='',
            audio_format='mp3',
			ascii=False,
   			coverart=False,
			ffmpeg='ffmpeg',
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
	def settings(cls):
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
