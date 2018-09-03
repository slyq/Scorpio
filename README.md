![Scorpio logo with a scorpion's tail](https://raw.githubusercontent.com/compileSuccess/Scorpio/master/scorpio.png?token=AfdmIr9eAiQF68iiEPRZChPt-YQnrcKrks5bkhlvwA%3D%3D)

# Scorpio

Scorpio is a Windows scoring engine tool designed to aid in the scoring of Windows virtual images. The primary purpose of the framework has been to make scoring security competitions as simple as possible, so that more time and energy may be spent setting up the competition environment itself. It has a clean detection and output of summary for vulnerabilities that are manually checked.

## Getting Started

Download the Scoring Engine folder to a virtual image.

### Prerequisites

You will need to use 64-bit Python 3.6. You also need to use a Windows system. Currently, the program has been tested to work on:

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

## Running the tests

Use a pre-built image to test the vulnerabilities to ensure that the scoring engine is scoring correctly.

## Known bugs that are features

* Disabling a user will prevent the password changed check for that user

## Built With

* [Python](https://www.python.org/) - The coding language used

## Authors

* **Jimmy Li** - [jimmyl02](https://github.com/jimmyl02)
* **Clement Chan** - [compileSuccess](https://github.com/compileSuccess)

## License

This project is not licensed under anything, but is under a private repos. If you are not one of the authors you shouldn't have access to this unless permitted for special reasons.

## Acknowledgments

* Thanks to Jared Flores for inspiration
