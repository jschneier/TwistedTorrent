from setuptools import setup, find_packages

__version__ = '0.5.1'
__author__ = 'Josh Schneier'

requires = [
    'twisted==13.0.0',
    'bitarray==0.8.0'
]

setup(
    name='Twisted Torrent',
    version=__version__,
    packages=find_packages(),
    install_requires=requires,
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    entry_points='''
    # -*- Entry points: -*-
    [console_scripts]
    torrent = twisted_torrent.scripts:do_torrent
    '''
)
