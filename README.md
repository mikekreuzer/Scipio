# Scipio

Scipio scripts the download & build of Cocoa frameworks. Scipio's offered as an alternative to Carthage and CocoaPods. Scipio uses the same sort of Cartfiles as Carthage and the basic workflow is the same:

1. Install Scipio
2. Create a Cartfile that lists the frameworks you’d like to use (ie it's a distributed system)
3. Type <code>scipio</code> and Scipio will fetch and build each framework you’ve listed
4. Then it's a matter of following the instructions on the pack - often times that's dragging the framework binaries into your application’s Xcode project & adding the binary statically or dynamically, but that bit's up to you, this isn't CocoaPods.

## CocoaPods, Carthage and Scipio.

<img align="right" src="Scipio_head.png" alt="Scipio Africanus" width="180" height="317">

Carthago delenda est!

[CocoaPods](http://cocoapods.org/) is the grandfather of dependency management for Cocoa. [Carthage](https://github.com/Carthage/Carthage) was created to be a decentralized alternative. Carthage was written in Swift, and not only Swift, but some of the more experimental bits of Swift.

I love Swift. I love the idea of Carthage, so I wrote Scipio, in Python. Python isn't going to get experimental again any time soon, and decoupling the language of this tool from the still rapidly changing language it's used to build means for (I hope) a lot less heartache.

## Installation

Scipio's a Python script, it should run in Python 2 or 3, and on a Mac you already have that installed. You'll also obviously need Xcode. To install Scipio, open terminal and type:

````bash
pip install scipio
````

## Usage

In the folder you want your frameworks built, create a file called 'Cartfile' with lines in the format:

```bash
github "Alamofire/AlamofireImage" ~>2.1
```

That's more or less the same format Carthage uses, though there are some differences. The version comparators supported are < <= = == >= > ~ and ~>

= and == are synonymous, but ~ and ~> aren't (see below for the differences to Carthage's Cartfiles).

Then cd to the folder and run Scipio from the terminal

````bash
scipio
````

Scipio will download the best match it can find from the tagged versions of the repository on Github and build the project/workspace. It doesn't have to be a framework, but building frameworks is the main use case. If the project has a Cartfile in it that framework will be downloaded and built first (and so on recursively).

You can pass along arguments at the command line to modify scipio or xcodebuild's behavior. Type <code>scipio -h</code> for the current list. If a target/scheme etc exists in the project or workspace it will be used. If it doesn't exist, or if no arguments are supplied then the defaults set up by a framework's authors' are used.

## Optional arguments

Flag             | Means
---------------- | ---------------------------------
-h, --help       | show this help message and exit
-down            | download & unzip but don't build
-plistb          | change all plist build numbers to this string
-plistv          | change all plist version numbers to this string
-project         | xcodebuild: project name
-workspace       | xcodebuild: workspace name
-configuration   | xcodebuild: configuration name
-scheme          | xcodebuild: scheme name
-sdk             | xcodebuild: sdk full path or canonical name
-target          | xcodebuild: project target name
-verbose         | xcodebuild will let you know, a lot
-v, --version    | show program's version number and exit

## Differences to Carthage

I'm not trying especially hard to support some of Carthage's design choices -- OGDL anyone? -- but I'm not trying to become incompatible either.

### Semantic version comparisons

Using Node, ~1.2 and ~1.2.0 for example both don't match 1.3. In Ruby ~>1.2.0 doesn't match 1.3, but ~>1.2 does. Scipio respects both ~ and ~>. Carthage doesn't. Carthage uses Ruby's ~> to mean Node's ~.

== and = can both be used to mean equals.

So far named tags aren't supported in place of version constraints (but I plan to).

### Non Github gits

Others gits are introduced with the word git in Carthage Cartfiles, in Scipio that's optional. (The other git functionality is completely untested so that may change.)

### Convenience methods

You can change the build and version numbers of all the projects you're building in one Cartfile to be the same, using the optional -plistb and -plistv flags. For a brief moment iTunes Connect seems to have required this, possibly in error. This doesn't work with download & unzip only, only for builds. As a philosophical aside, this is a little CocoaPods-like for my taste. Use is eg

````bash
scipio -plistv 42.0.0
````

## Contact

- [Twitter](https://twitter.com/mikekreuzer)
- [GitHub](https://github.com/mikekreuzer/)

## Credits

Carthage and Cocoapods, obviously. Miguel Hermoso for the [picture of Scipio](https://commons.wikimedia.org/wiki/File:Escipión_africano.JPG) looking existentially disappointed.

## License

The picture of Scipio is [CC Attribution-ShareAlike 3.0 Unported](https://creativecommons.org/licenses/by-sa/3.0/deed.en)

Everything else: [MIT](http://opensource.org/licenses/MIT)

## History & Plans

### 0.1.0 -- 5 September 2015

- initial release
- bread & butter: download and build Xcode projects from Github

### 0.1.1 -- 6 September 2015

- added missing ABOUT.rst file and manifest
- version incorrectly calls itself 0.1.0

### 0.2.0 -- 8 September 2015

-  added more semantic version constraints, Ruby's ~> Node's ~ and =
-  abandoned too slavish a compatibility with Carthage (eg not using ~> to mean ~)
-  better docs

### 0.2.1 -- 15 September 2015

- fixed a bug with semver comparison (greater than or equals to typo)

### 0.2.2 -- 26 September 2015

- fixed the lack of unit tests - starting with 92% coverage of test_download
- fixed ignoring the optional (optional in Scipio) word 'git' in front of non-GitHub git URLs in Cart files
- changed the name of the ABOUT.rst file to README.rst

### 0.3.0 -- 25 October 2015

- added the optional -down flag, to download & unzip files without Scipio attempting to build them
- added the tests written so far to the PyPI distribution
- README.rst better reflects README.md
- mistakenly includes the -cart flag

### 0.4.0 -- 26 October 2015

- added optional -plistb and -plistv flags
- fixed the extraneous -cart flag

###  0.4.1 -- 1 November 2015

- added some more unit tests, have 60% coverage
- version's only recorded in the one place now
- scripted my setup.py setup, in config.py
- missing VERSION file causes CTD

###  0.4.2 -- 1 November 2015

- VERSION added to package_data in setup.py

###  Next

- optional -cart flag, to supply the download target via the command line, as a convenient replacement for one line Cart files
- support for named tags
- better (ie some!) error messages
- 95% test coverage
- optional recursion depth limits
- circular dependency checks
- duplicate download checks
- look into how non Github gits work properly
- possible tie in to other (Ruby?) build automation - composable build tools are good build tools
