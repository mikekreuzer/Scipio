"""Parse a cartfile, work out the verion that best satisfies the
constraints given, download & extract that zipball"""

from collections import namedtuple
import json
from re import match, sub, VERBOSE
from os import makedirs, path
import zipfile

import requests
import semantic_version

Project = namedtuple('Project', 'folder, workspace_files, project_files')
Target = namedtuple('Target', 'server, repository, constraint')

def parse_cart_file():
    """Extract a list of download target from lines in a cartfile"""
    if path.isfile('Cartfile.resolved'):
        file_name = 'Cartfile.resolved'
        cartfile_resolved = True
    elif path.isfile('Cartfile'):
        file_name = 'Cartfile'
        cartfile_resolved = False
    else:
        return []
    with open(file_name) as in_file:
        targets = []
        for line in in_file:
            attribs = match(r'^(\S+|".+")\s+("\S+")\s+(.*)$', line)
            if not attribs:
                continue
            ser, rep, con = attribs.groups()
            targets.append((cartfile_resolved, Target(server=ser.strip('"\' '),
                                                      repository=rep.strip('"\' '),
                                                      constraint=con.strip('"\' '))))
        return targets


def get_tags(download_target):
    """Get the tagged versions of the of the targetted repo"""
    if download_target.server == "github":
        api_address = "https://api.github.com/repos/" + download_target.repository + "/tags"
    else:
        api_address = sub(r'^\s*git\s', '', download_target.server, count=1)
        api_address = api_address + download_target.repository + "/tags"
    result = requests.get(api_address)
    if result.ok:
        tags = json.loads(result.text or result.content)
        return tags
    else:
        return None


def more_relaxed_semver(relaxed_version):
    """Deal with some less formally correct version numbers than the semantic_version module"""
    version = match(r'''^(?:\s*v?\s*)
                     (?P<major>\d*)\.
                     (?P<minor>\d*)
                     (?:\.(?P<patch>\d*))?
                     (?P<text>[0-9A-Za-z\-\+\.]*)?$''', relaxed_version, VERBOSE)
    if version:
        if version.group('major'):
            ver = version.group('major')
            if version.group('minor'):
                ver = ver + '.' + version.group('minor')
                if version.group('patch'):
                    ver = ver + '.' + version.group('patch')
                    if version.group('text'):
                        ver = ver + version.group('text')
                else:
                    ver = ver + '.0'
            else:
                ver = ver + '.0.0'
            try:
                semantic_version.Version(ver, partial=True)
            except ValueError:
                ver = '0.0.0'
            return ver
        else:
            return '0.0.0'
    else:
        return '0.0.0'


def more_relaxed_comparison(relaxed_comparator):
    """Deal with Ruby's ~>, Node's ~, and everyone's =
    using Node ~1.2 and ~1.2.0 both don't match 1.3
    in Ruby ~>1.2.0 doesn't match 1.3, but ~>1.2 does
    NB this is different to how Carthage does it, Carthage uses ~> to mean ~"""
    match_str = match(r'^(?P<comparator><=|<|==|>=|=|>|~>|~)+(?:\s*)?(?P<version>.+)$',
                      relaxed_comparator)
    if match_str:
        comp = match_str.group('comparator')
        val = more_relaxed_semver(match_str.group('version'))
        if comp in ['<', '<=', '==', '>=', '>']:
            return comp + val
        elif comp is '=':
            return '==' + val
        elif comp == '~' or comp == '~>':
            out = '>=' + val + ',<'
            ver = semantic_version.Version(more_relaxed_semver(val), partial=True)
            if comp == '~>' and match_str.group('version').count('.') == 1:
                out += '='
            if ver.patch == 0 and ver.minor == 0:
                upper = str(ver.next_major())
            else:
                upper = str(ver.next_minor())
            return out + upper
        else:
            return '>=' + str(val)
    else:
        return '>=0.0.0'


def calc_best_version_address(tags, constraint, record_str, cartfile_resolved):
    """Calculate the address of the of the best version with or without constraints,
    including a particular specific version"""
    versions = [semantic_version.Version(more_relaxed_semver(tag['name']), partial=True)
                for tag in tags]
    try:
        specification = semantic_version.Spec(more_relaxed_comparison(constraint))
    except ValueError:
        specification = semantic_version.Spec('>0.0.0')
    best = specification.select(versions)
    if best:
        for tag_info in tags:
            if best == semantic_version.Version(more_relaxed_semver(tag_info['name']),
                                                partial=True):
                #record this
                version = str(best)
                if not cartfile_resolved:
                    with open('Cartfile.resolved', 'a') as write_file:
                        write_file.write(record_str + ' ==' + version + '\n')
                return tag_info['zipball_url'], version
    else:
        return None, None


def download_and_extract(the_file, the_path, version):
    """Download this file & extract its contents to path, return info on the project"""
    names = the_path.split('/')
    temp_filename = the_path + '-' + version + '.zip'
    folder = names[0]
    if not path.exists(folder):
        makedirs(folder)
    # download
    resp = requests.get(the_file, stream=True)
    with open(temp_filename, 'wb') as download:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                download.write(chunk)
                download.flush()
    # extract
    with zipfile.ZipFile(temp_filename) as myzip:
        myzip.extractall(folder)
        content_list = myzip.namelist()
        folder_list = [name for name in content_list if name.endswith('/')]
        workspaces = [name.rstrip('/') for name in folder_list
                      if name.endswith('.xcworkspace/') and not
                      name.endswith('.xcodeproj/project.xcworkspace/')]
        projects = [name.rstrip('/') for name in folder_list if name.endswith('.xcodeproj/')]
        return Project(folder=folder,
                       workspace_files=workspaces,
                       project_files=projects)
