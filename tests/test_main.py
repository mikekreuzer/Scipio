"""tests for main.py -- just placeholders for now"""
from nose import with_setup

from scipio.main import parse_args

def test_parser():
    """Options load"""
    parser = parse_args(['-project', 'pr', \
                         '-cart', 'ca', \
                         '-down', \
                         '-workspace', 'wo', \
                         '-configuration', 'co', \
                         '-scheme', 'sc', \
                         '-sdk', 'sd', \
                         '-target', 'ta', \
                         '-verbose'])
    assert vars(parser) == {'cart': 'ca', \
                            'configuration': 'co', \
                            'down': True, \
                            'project': 'pr', \
                            'scheme': 'sc', \
                            'sdk': 'sd', \
                            'target': 'ta', \
                            'verbose': True, \
                            'workspace': 'wo'}

    # more to follow
