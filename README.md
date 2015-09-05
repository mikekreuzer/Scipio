# Scipio

Carthago delenda est!

<img align="right" src="Scipio_head.png" alt="Scipio Africanus">

Scipio scripts the download & build of Cocoa frameworks. Scipio's offered as an alternative to Carthage and CocoaPods.

Scipio uses the same Cartfiles as Carthage and the basic workflow is the same:

1. Install Scipio
2. Create a Cartfile that lists the frameworks you’d like to use
3. Type <code>scipio</code> and Scipio will fetch and build each framework you’ve listed
4. Drag the framework binaries into your application’s Xcode project

## CocoaPods, Carthage and Scipio.

[CocoaPods](http://cocoapods.org/) is the grandfather of dependency management for Cocoa. [Carthage](https://github.com/Carthage/Carthage) was created to be a decentralized alternative. Carthage was written in Swift, and not only Swift, but some of the most experimental bits of Swift. I love Swift. I love the idea of Carthage, so I wrote Scipio, in Python. Python isn't going to get experimental again any time soon, and decoupling the language of this tool and the still rapidly changing language it's used to build means for (I hope) a lot less heartache.

## Installation

Scipio's a Python script, it should run in Python 2 or 3, and on a Mac you already have that installed. In your terminal type:

````bash
pip install scipio
````

## Usage

In the folder you want your frameworks built, create a file called 'Cartfile' with lines in the format:

```ogdl
github "Alamofire/Alamofire" >=2.0.0-beta.2
```

That's the same format Carthage uses, though the ~ comparison operator isn't supported yet. You can use < <= == => and >

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
-project         | xcodebuild: project name
-workspace       | xcodebuild: workspace name
-configuration   | xcodebuild: configuration name
-scheme          | xcodebuild: scheme name
-sdk             | xcodebuild: sdk full path or canonical name
-target          | xcodebuild: project target name
-verbose         | xcodebuild will let you know, a lot
-v, --version    | show program's version number and exit

## Credits

Carthage and Cocoapods, obviously. Miguel Hermoso for the [picture of Scipio](https://commons.wikimedia.org/wiki/File:Escipión_africano.JPG) looking existentially disappointed.

## License

The picture of Scipio is [CC Attribution-ShareAlike 3.0 Unported](https://creativecommons.org/licenses/by-sa/3.0/deed.en)

Everything else: [MIT](http://opensource.org/licenses/MIT)

## History & Plans

- 0.1.0 -- Initial release, 5 September 2015
  - [x] bread & butter: download and build Xcode projects from Github
  - [x] stable (hopefully, so far)
- 0.1.1 -- 6 September 2015
  - [x] added missing ABOUT.rst file and manifest
- Next
  - [ ] update ABOUT.rst to fix a typo (done on github)
  - [ ] unit tests
  - [ ] better (ie some) error messages
  - [ ] more semver constraints, support Ruby's ~> and Node's ~ and everyone's =
  - [ ] optional recursion depth limits
  - [ ] circular dependency checks
  - [ ] duplicate download checks
  - [ ] better OGDL parsing / maybe some alternative to that
  - [ ] possible tie in to other (Ruby?) build automation
