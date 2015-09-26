"""Tests for download.py"""
from collections import namedtuple
from os import remove
from io import BytesIO as StringIO
import shutil
import zipfile

from nose import with_setup
from nose.tools import assert_raises
import responses
import requests

from scipio.download import parse_cart_file, get_tags, more_relaxed_semver, \
                            more_relaxed_comparison, calc_best_version_address, download_and_extract

Project = namedtuple('Project', 'folder, workspace_files, project_files')
Target = namedtuple('Target', 'server, repository, constraint')


def setup_cartfile():
    """Create a cartfile to parse"""
    with open('Cartfile', 'a') as the_file:
        the_file.write('github "Alamofire/Alamofire" >=2.0.0-beta.2')


def setup_garbled_cartfile():
    """Create a garbles cartfile to parse"""
    with open('Cartfile', 'a') as the_file:
        the_file.write('this is not what we want\nat all')


def teardown_cartfile():
    """Delete the test Cartfile"""
    remove('Cartfile')


def also_setup_resolved_cartfile():
    """Create a resolved cartfile to parse too"""
    setup_cartfile()
    with open('Cartfile.resolved', 'a') as the_file:
        the_file.write('github "mikekreuzer/Scipio" ==0.3.0')


def also_teardown_resolved_cartfile():
    """Delete the test resolved Cartfile too"""
    teardown_cartfile()
    remove('Cartfile.resolved')


@with_setup(setup_cartfile, teardown_cartfile)
def test_parse_cart_file():
    """Extract a list of download target from lines in a cartfile"""
    assert parse_cart_file() == [(False,
                                  Target(server='github',
                                         repository='Alamofire/Alamofire',
                                         constraint='>=2.0.0-beta.2'))]


@with_setup(also_setup_resolved_cartfile, also_teardown_resolved_cartfile)
def test_parse_resolved_cart_file():
    """Extract a list of download target from lines in a resolved cartfile"""
    assert parse_cart_file() == [(True,
                                  Target(server='github',
                                         repository='mikekreuzer/Scipio',
                                         constraint='==0.3.0'))]


def test_parse_cart_file_missing():
    """Extract a list of download targets fails with no cartfile"""
    assert parse_cart_file() == []


@with_setup(setup_garbled_cartfile, teardown_cartfile)
def test_parse_cart_file_garbled():
    """Extract a list of download targets fails with unparse-able cartfile"""
    assert parse_cart_file() == []


@responses.activate
def test_get_tags_github():
    """Get the tagged versions of the targetted github repo"""
    target = Target(server='github', repository='mikekreuzer/Scipio', constraint='>=0.2.0')

    responses.add(responses.GET, 'https://api.github.com/repos/mikekreuzer/Scipio/tags',
                  body='[{"fail": "fail"}]',
                  status=500,
                  content_type='application/json')

    assert None == get_tags(target)


@responses.activate
def test_get_tags_fail_github():
    """Fail to get the tagged versions of the targetted github repo"""
    target = Target(server='github', repository='mikekreuzer/Scipio', constraint='>=0.2.0')

    responses.add(responses.GET, 'https://api.github.com/repos/mikekreuzer/Scipio/tags',
                  body='[{\
                        "name": "0.2.1",\
                        "zipball_url": "https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.2.1",\
                        "tarball_url": "https://api.github.com/repos/mikekreuzer/Scipio/tarball/0.2.1",\
                        "commit": {\
                        "sha": "a3f9a6641ab6c417b5afb245ac19ddb3e2ec45b5",\
                        "url": "https://api.github.com/repos/mikekreuzer/Scipio/commits/a3f9a6641ab6c417b5afb245ac19ddb3e2ec45b5"\
                        }}]',
                  status=200,
                  content_type='application/json')

    resp = requests.get('https://api.github.com/repos/mikekreuzer/Scipio/tags')
    assert resp.json() == get_tags(target)


# need to read up on non github gits & test that behaviour too


def test_semver_3_parts():
    """Deal with some less formally correct version numbers - 3 parts"""
    assert more_relaxed_semver('0.3.0') == '0.3.0'


def test_semver_2_parts():
    """Deal with some less formally correct version numbers - 2 parts"""
    assert more_relaxed_semver('0.3') == '0.3.0'


def test_semver_1_part():
    """Deal with some less formally correct version numbers - 1 part"""
    assert more_relaxed_semver('3') == '0.0.0' # could make this 3.0.0


def test_semver_1_part_point():
    """Deal with some less formally correct version numbers - 1 part"""
    assert more_relaxed_semver('3.') == '3.0.0'


def test_semver_3_parts_v():
    """Deal with some less formally correct version numbers - 3 and v"""
    assert more_relaxed_semver('v0.3.0') == '0.3.0'


def test_semver_2_parts_v():
    """Deal with some less formally correct version numbers - 2 and v"""
    assert more_relaxed_semver('v0.3') == '0.3.0'


def test_semver_beta():
    """Deal with some less formally correct version numbers - beta"""
    assert more_relaxed_semver('v2.3.0-beta.2') == '2.3.0-beta.2'


def test_semver_named():
    """Deal with some less formally correct version numbers - named tags"""
    assert more_relaxed_semver('named_tags_later') == '0.0.0'


def test_semver_garbled():
    """Deal with some less formally correct version numbers - garbled tags"""
    assert more_relaxed_semver('0.0.0.0.0.0') == '0.0.0'


def test_semver_blank():
    """Deal with some less formally correct version numbers - blank tags"""
    assert more_relaxed_semver('') == '0.0.0'


def test_comparison_node_3_parts():
    """Compare with Node's ~ and 3"""
    assert more_relaxed_comparison('~1.2.0') == '>=1.2.0,<1.3.0'


def test_comparison_node_2_parts():
    """Compare with Node's ~ and  2"""
    assert more_relaxed_comparison('~1.2') == '>=1.2.0,<1.3.0'


def test_comparison_ruby_3_parts():
    """Compare with Ruby's ~> and 3"""
    assert more_relaxed_comparison('~>1.2.0') == '>=1.2.0,<1.3.0'


def test_comparison_ruby_two_parts():
    """Compare with Ruby's ~> and 2"""
    assert more_relaxed_comparison('~>1.2') == '>=1.2.0,<=1.3.0'


def test_comparison_greater():
    """Compare with greater than"""
    assert more_relaxed_comparison('>2.0') == '>2.0.0'


def test_comparison_less():
    """Compare with less than"""
    assert more_relaxed_comparison('<2.0') == '<2.0.0'


def test_comparison_greater_equals():
    """Compare with greater than or equals to"""
    assert more_relaxed_comparison('>=2.0') == '>=2.0.0'


def test_comparison_less_equals():
    """Compare with less than or equals to"""
    assert more_relaxed_comparison('<=2.0.0') == '<=2.0.0'


def test_comparison_one_equals():
    """Compare with ="""
    assert more_relaxed_comparison('=2.0.0-beta.2') == '==2.0.0-beta.2'


def test_comparison_assignment_beta():
    """Compare with = space v and beta"""
    assert more_relaxed_comparison('= v2.0.0-beta.2') == '==2.0.0-beta.2'


def test_comparison_equals():
    """Compare with =="""
    assert more_relaxed_comparison('==2.0.0') == '==2.0.0'


def test_comparison_gibberish():
    """Compare using gibberish"""
    assert more_relaxed_comparison('makes no sense') == '>=0.0.0'


SLACK_TAGS = [{'name': '0.0.1',
               'zipball_url': 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/'},
              {'name': 'v1.3.0',
               'zipball_url': 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/1.3.0/'},
              {'name': 'master',
               'zipball_url': 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/master/'},
              {'name': 'test-iPh',
               'zipball_url': 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/test-iPh/'},
              {'name': '2.0.0-beta',
               'zipball_url': 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/2.0-beta/'}]


def test_best_version():
    """Get the address of the of the best version with constraints"""
    slack_constraint = '~1.3'
    record_str = 'greatProject'
    cartfile_resolved_so_no_file = True

    assert ('https://api.github.com/repos/mikekreuzer/Scipio/zipball/1.3.0/', '1.3.0') == \
            calc_best_version_address(SLACK_TAGS,
                                      slack_constraint,
                                      record_str,
                                      cartfile_resolved_so_no_file)


def test_best_version_no_constraint():
    """Get the address of the of the best version without constraints"""
    slack_constraint = ''
    record_str = 'greatProject'
    cartfile_resolved_so_no_file = True
    assert ('https://api.github.com/repos/mikekreuzer/Scipio/zipball/2.0-beta/', '2.0.0-beta') == \
            calc_best_version_address(SLACK_TAGS,
                                      slack_constraint,
                                      record_str,
                                      cartfile_resolved_so_no_file)


def test_best_version_specific():
    """Get the address of a particular version"""
    slack_constraint = '==0.0.1'
    record_str = 'greatProject'
    cartfile_resolved_so_no_file = True
    assert ('https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/', '0.0.1') == \
            calc_best_version_address(SLACK_TAGS,
                                      slack_constraint,
                                      record_str,
                                      cartfile_resolved_so_no_file)


def test_best_version_none_satisfy():
    """Get the address of the of the best version with impossible constraints"""
    slack_constraint = '>5.0.0'
    record_str = 'greatProject'
    cartfile_resolved_so_no_file = True
    assert (None, None) == \
            calc_best_version_address(SLACK_TAGS,
                                      slack_constraint,
                                      record_str,
                                      cartfile_resolved_so_no_file)


def teardown_zipfile():
    """Delete the test zipfile"""
    try:
        remove('test_file-0.0.1.zip')
    except OSError:
        pass


@responses.activate
@with_setup(None, teardown_zipfile)
def test_extract_bad_zipfile():
    """Download this file & try (& fail) to extract its contents to path"""
    a_file = 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/'
    a_path = './test_file'
    a_version = '0.0.1'
    responses.add(responses.GET, 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/',
                  body='[{"json": "not a zip file"}]',
                  status=200,
                  content_type='application/zip')

    with assert_raises(zipfile.BadZipfile):
        download_and_extract(a_file, a_path, a_version)


def teardown_zipfolder():
    """Delete the test zipfile"""
    shutil.rmtree('./test_download/')


@responses.activate
@with_setup(None, teardown_zipfolder)
def test_extract_good_zipfile():
    """Download this file & extract its contents to path, return info on the project"""
    # create a zip file in memory
    in_memory_data = StringIO()
    z_file = zipfile.ZipFile(in_memory_data, "w", zipfile.ZIP_DEFLATED, False)
    z_file.writestr("has spaces really.xcodeproj/", "")
    z_file.writestr("and-not.project.xcworkspace/", "")
    for file in z_file.filelist:
        file.create_system = 0
    z_file.close()
    zip_string = in_memory_data.getvalue()

    responses.add(responses.GET, 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/',
                  body=zip_string,
                  status=200,
                  content_type='application/zip')

    a_file = 'https://api.github.com/repos/mikekreuzer/Scipio/zipball/0.0.1/'
    a_path = 'test_download/test_file'
    a_version = '0.0.1'

    assert download_and_extract(a_file, a_path, a_version) == \
           Project(folder='test_download',
                   workspace_files=['and-not.project.xcworkspace'],
                   project_files=['has spaces really.xcodeproj'])
