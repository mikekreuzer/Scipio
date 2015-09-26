"""Setup for the scipio module"""
from setuptools import setup
from os import path

ROOT = path.dirname(path.realpath(__file__))

with open(path.join(ROOT, 'README.rst')) as f:
    LONG_DESC = f.read()

setup(
    name='scipio',
    version='0.2.2',
    description='Automate github downloads and xcodebuild',
    long_description=LONG_DESC,
    url='https://github.com/mikekreuzer/scipio',
    author='Mike Kreuzer',
    author_email='motherfunctor@yahoo.com.au',
    platforms=["osx"],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': ['scipio=scipio.command_line:main'],
    },
    keywords='xcode xcodebuild github Carthage Cocoapods',
    packages=['scipio'],
    install_requires=['requests', 'semantic_version'],
    tests_require=['nose', 'responses']
)
