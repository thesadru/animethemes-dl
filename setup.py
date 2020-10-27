#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='animethemes-dl',
    version='1.0.1',
    author='thesadru',
    author_email='add_your_email_here@gmail.com',
    description='Downloads anime themes from theme.moe using an animethemes-api. Supports Batch download and MAL connecting.',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    url='https://github.com/thesadru/animethemes-dl',
    keywords=['anime', 'opening', 'ending', 'download', 'hd'],
    install_requires=[
        'pySmartDl',
        'eyed3',
        'requests',
        'colorama'
    ],
    extras_require={},
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        animethemes-dl=animethemes_dl.main:batch_download
    '''
)
