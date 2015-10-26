"""tests for main.py -- just placeholders for now"""
from nose import with_setup

from scipio.main import parse_args

def test_parser():
    """Options load"""
    parser = parse_args(['-project', 'pr', \
                         '-down', \
                         '-plistb', '0.0.1', \
                         '-plistv', '0.0.2', \
                         '-workspace', 'wo', \
                         '-configuration', 'co', \
                         '-scheme', 'sc', \
                         '-sdk', 'sd', \
                         '-target', 'ta', \
                         '-verbose'])
    assert vars(parser) == {'sdk': 'sd',
                            'verbose': True,
                            'plistv': '0.0.2',
                            'plistb': '0.0.1',
                            'scheme': 'sc',
                            'project': 'pr',
                            'configuration': 'co',
                            'down': True,
                            'target': 'ta',
                            'workspace': 'wo'}

    # more to follow
