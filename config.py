"""
automate the setup for setup.py - requires: pandoc, setuptools, & twine
not part of scipio, just what I use to build it
"""
import argparse
from os import path
import subprocess
from sys import argv

def parse_args(args):
    """Command line switches"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-prod', help='upload using twine',
                        required=False, action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version', version=_VERSION)
    return parser.parse_known_args(args)[0]

with open('./scipio/VERSION', 'r') as version_file:
    _VERSION = version_file.read().replace('\n', '')

_ARGS = parse_args(argv[1:])

# uninstall
subprocess.call(['pip', 'uninstall', 'scipio'])

# generate the RST version of the Readme file
subprocess.call(['pandoc', '--from=markdown_github+raw_html', '--to=rst',
                 '--no-wrap', '--output=README.rst', 'README.md'])

# build
subprocess.call(['python', 'setup.py', 'sdist'])

if _ARGS.prod:
    # upload
    subprocess.call(['twine', 'upload', 'dist/scipio-%(ver)s.tar.gz' %
                     {'ver': _VERSION}])
else:
    # install a local version
    subprocess.call(['pip', 'install', '-e', path.dirname(path.abspath(__file__))])
