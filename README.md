![Scorpio logo with a scorpion's tail](https://github.com/compileSuccess/Scorpio/blob/master/scorpio.png)

# Scorpio

Scorpio is a Windows scoring engine tool designed to aid in the scoring of Windows virtual images. The primary purpose of the framework has been to make scoring security competitions as simple as possible, so that more time and energy may be spent setting up the competition environment itself. It has a clean detection and output of summary for vulnerabilities that are automatically checked.

## Getting Started

(Optional) Modify the .gitattributes to fit what you want to export. Then, download the Scorpio-master.zip to a virtual image. See the [getting started](https://github.com/compileSuccess/Scorpio/wiki/Getting-Started) page for more details.

### Prerequisites

You will need to use 64-bit Python 3.6. You also need to use a Windows system. Currently, the program has been tested to work on:

* Windows 8.1
* Windows 10

You will also need pywin32 and pyinstaller to modify/test and export the scoring engine as a standalone.
To install the needed modules simply run:

```
$ pip install pywin32
$ pip install pyinstaller
```

## Modifying the Engine to Your Purposes

See the wiki.

Don't forget to test the engine (run as admin) to see if it runs without errors.

Once you are done, use pyinstaller to build an executable and add an icon and obfuscation through [Cython](http://cython.org/) if you desire.

```
$ pyinstaller --onefile -windowed -i scorpio.ico scorpio.py
```

Note that `-windowed` may cause some issues with your program, depending on your vulnerabilities.

## Running the tests

Use a pre-built image or build a new one to test the vulnerabilities to ensure that the scoring engine is scoring correctly. Pretend that you are the client/user for better results (they may think one thing whereas you think another). Ensure that clients/users cannot accidentally mess up the engine.

## Putting the stuff on your image

* Store the wav (and jpg - optional) files in a new folder wherever you desire. Make sure you specify the path in your scoring engine
* Store the exe and ico inside the Windows folder or any folder where clients won't look at normally, and possibly add hide attributes
* Create a shortcut for the exe and put it on the desktop
* Change the shortcut icon to the ico file
* Implement your own readme, and make sure to mention NOT TO DELETE SCORPIO
* Implement the forensics questions
* Create a scheduled task to run with highest privileges on log in
* Run it several times to test it out
* Delete the Scorpio-master.zip and its extraction folder. LEAVE NO TRACE TO THE SOURCE CODE!

## Known bugs that are dismissed

* Disabling a user will prevent the password changed check for that user
* Sometimes you may have to manually open the features box so that `dism` gets the list

## Fun Stats/Facts

A FeatureObject takes the longest time to check, and the time it takes is inconsistent.
The time for a run through vuln.check for all vulns can vary from ~0.04-0.20s from one FeatureObject.

## Built With

* [Python 3.6.6](https://www.python.org/downloads/release/python-366/) - The coding language used

## The Scorpio Team

* **Clement Chan** Director, Lead Developer, Web Developer - [compileSuccess](https://github.com/compileSuccess)
* **Jimmy Li** Server Developer and Host - [jimmyl02](https://github.com/jimmyl02)

## License

This project is not licensed under anything, but it is a private repos. If you are not one of the authors you shouldn't have access to this unless permitted for special reasons.

## Acknowledgments

* Thanks to Jared Flores and Allen Stubblefield for inspiration
* Thanks to Jino Sirivatanarat for image supplementations
