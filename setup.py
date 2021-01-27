from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='animethemes-dl',
    version='2.2.0',
    author='thesadru',
    author_email='dan0.suman@gmail.com',
    license='MIT License',
    description='Downloads anime themes from animethemes.moe. Supports Batch download and animelist connecting.',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # download_url='https://github.com/thesadru/animethemes-dl/archive/master.zip',
    python_requires='>=3.8',
    url='https://github.com/thesadru/animethemes-dl',
    keywords='mal anilist themes animethemes moe batch audio filter hd song api ffmpeg dl download songs'.split(),
    install_requires=["pySmartDl", "mutagen", "requests", "colorama"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        animethemes-dl=animethemes_dl.main:main
    '''
)
