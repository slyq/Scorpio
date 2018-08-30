# Windows Scoring Engine

The Windows Scoring Engine is a python program designed to aid in the scoring of Windows virtual images. It has a clean detection and output of vulnerabilities that are manually checked.

## Getting Started

Download the Scoring Engine folder to a virtual image.

### Prerequisites

You will need to use 64-bit Python 3.6. You also need to use a Windows system. Currently, the program has been tested to work on:

* Windows 10

You will also need pywin32 and pyinstaller to modify/test and export the scoring engine as a standalone.
To install the needed modules simply run:

```
> pip install pywin32
> pip install pyinstaller
```

## Modifying the Engine to Your Purposes

See the wiki.

Don't forget to test the engine (run as admin) to see if it runs without errors.

## Running the tests

Use a pre-built image to test the vulnerabilities to ensure that the scoring engine is scoring correctly.

## Built With

* [Python](https://www.python.org/) - The coding language used

## Authors

* **Jimmy Li** - [jimmyl02](https://github.com/jimmyl02)
* **Clement Chan** - [compileSuccess](https://github.com/compileSuccess)

## License

This project is not licensed under anything, but is under a private repos. If you are not one of the authors you shouldn't have access to this unless permitted for special reasons.

## Acknowledgments

* Thanks to Jared Flores for inspiration
