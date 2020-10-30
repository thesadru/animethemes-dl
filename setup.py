from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

with open('version', 'r') as f:
    version = f.read()

with open('requirements.txt','r') as f:
    install_requires = [i.strip('\n') for i in f.readlines()]

setup(
    name='animethemes-dl',
    version=version,
    author='thesadru',
    author_email='dan0.suman@gmail.com',
    description='Downloads anime themes from theme.moe using an animethemes-api. Supports Batch download and MAL connecting.',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    url='https://github.com/thesadru/animethemes-dl',
    keywords='download, anime, themes, animethemes, themes.moe, api, batch, hd, audio, filter, mal, al, myanimelist'.split(', '),
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        animethemes-dl=animethemes_dl.main:main
    '''
)