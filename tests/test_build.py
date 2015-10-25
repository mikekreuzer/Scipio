"""Tests for build.py -- just placeholders for now"""
from nose import with_setup

from scipio.build import parse_xcodebuild_list, run_build, setup_build, build_project_or_workspace

def test_parse_xcodebuild_list():
    """Decompose xcode -list output to lists"""
    # parse_xcodebuild_list(output_string)


def test_run_build():
    """Run the build command through xcodebuild"""
    # run_build(command, verbose, project)


def test_setup_build():
    """Go to the folder/project or folder/workspace and check if any of the configuration, sdk,
    scheme, or target args supplied exist in it, set up the build with as many of them as do"""
    # setup_build(project, possible_args, workspace=False)


def test_build_project_or_workspace():
    """Try to build the workspace or project specified via command-line arguments, passing on
    any arguments provided. Otherwise try to build the first scheme for the first workspace found,
    and if there isn't a workspace, the first project."""
    # build_project_or_workspace(project, args)
