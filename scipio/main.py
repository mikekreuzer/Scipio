"""- Parse a cartfile, work out the verion that best satisfies the
constraints given, download & extract that zipball, repeat this
recursively
- then build these things using xcodebuild"""

import argparse
from glob import glob
from os import chdir, getcwd, path

from build import build_project_or_workspace
from download import parse_cart_file, get_tags, get_best_version_address, download_and_extract

PARSER = argparse.ArgumentParser(description='Parse a cartfile, work out the \
                                 verion that best satisfies the constraints given, \
                                 download & extract that zipball, repeat this recusively, \
                                 then build these things using xcodebuild',
                                 epilog="Carthago delenda est")
PARSER.add_argument('-project', help='xcodebuild: project name',
                    required=False, metavar='')
PARSER.add_argument('-workspace', help='xcodebuild: workspace name',
                    required=False, metavar='')
PARSER.add_argument('-configuration', help='xcodebuild: configuration name',
                    required=False, metavar='')
PARSER.add_argument('-scheme', help='xcodebuild: scheme name',
                    required=False, metavar='')
PARSER.add_argument('-sdk', help='xcodebuild: sdk full path or canonical name',
                    required=False, metavar='')
PARSER.add_argument('-target', help='xcodebuild: project target name',
                    required=False, metavar='')
PARSER.add_argument('-verbose', help='xcodebuild will let you know, a lot',
                    required=False, action='store_true', default=False)
PARSER.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
ARGS = PARSER.parse_args()

def scipio():
    """Download repos and build them recursively"""
    scipio_wd = getcwd()
    line = parse_cart_file()
    for cartfile_resolved, download_target in line:
        if download_target:
            tags = get_tags(download_target)
            if tags:
                if not cartfile_resolved:
                    line_str = download_target.server + ' "' +download_target.repository + '"'
                else:
                    line_str = ''
                url, version = get_best_version_address(tags,
                                                        download_target.constraint,
                                                        line_str,
                                                        cartfile_resolved)
                if url:
                    project_info = download_and_extract(url, download_target.repository, version)

                    #peek ahead, look for cart files, if there are any dig deeper
                    child_folder = download_target.repository.split('/')[0]
                    seeking = './' + child_folder + '/*/Cartfile'
                    child_cart = glob(seeking)
                    if not child_cart:
                        child_cart = glob(seeking + '.resolved')
                    if child_cart:
                        chdir(path.dirname(child_cart[0]))
                        scipio()
                        chdir(scipio_wd)
                    build_project_or_workspace(project_info, ARGS)
