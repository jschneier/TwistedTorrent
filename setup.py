from setuptools import setup, find_packages
import twistedtorrent

with open('./requirements.txt', 'r') as r:
    requires = r.read().split()

with open('./README.md', 'r') as r:
    readme = r.read()

setup(
    name='Twisted Torrent',
    version=twistedtorrent.__version__,
    packages=find_packages(),
    install_requires=requires,
    long_description=readme,
    license='MIT',
    entry_points='''
    # -*- Entry points: -*-
    [console_scripts]
    torrent = twistedtorrent.scripts:do_torrent
    '''
)
