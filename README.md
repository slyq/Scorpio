![Scorpio logo](https://drive.google.com/uc?export=view&id=1nvj9XO6RMVa9YdkFLhZKwaxZeizdWCpS)

# Scorpio

Scorpio is a client-side Windows vulnerability scoring engine tool designed to score the security of Windows machines given predefined vulnerabilities to check for. It is meant to mock CyberPatriot image scoring, and it provides a clean output of the security issues that are fixed.

| :warning: DISCLAIMER                                                                                                                                                                                                      |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Scorpio is designed for educational purposes, not for competitions! Scoring happens offline, but that also means that with enough effort, scores can be faked and vulnerabilities can be extracted. Use at your own risk! |

## Screenshots

Standard usage:

![Standard usage](https://drive.google.com/uc?export=view&id=1rRZL0NkVnDfVWVCmW3Xtx7ogT-_EvgM4)

Backdoor usage:

![Backdoor usage](https://drive.google.com/uc?export=view&id=1JlYWMuCj8_4x_6S0_IPYEGHgv7HKJoRm)

## Features

- GUI editor for your vulnerability assessment configuration
- Friendly output of remediatead security issues
- Visual and audio notifications upon point gain/loss
- Backdoor mode for debugging and answer key hints

## Prerequisites

Install Python 3.11. You also need to use a Windows system.

Install the required Python modules:

```sh
pip install -r requirements.txt
```

### Configuration Editor

The configuration tool for Scorpio has been migrated to an electron app. It can be downloaded [here](https://drive.google.com/file/d/1WGncgS5qvgRrWK09IVnO-MkPiYfeC9ao/view?usp=sharing).

## Usage

* Move the "Scoring Engine" folder to "C:\Scoring Engine".
* Use the configuration editor to generate an encrypted configuration for the vulnerabilities, and paste it into the `conf.txt`. Run `scorpio.py` with an administrative account.
* Use the forensics question template to implement your own forensics questions.
* Create an `env.py` from the `env.example.py`, supplying your own codes. If you really need it, ask the developers for the key.

To build an exe, simply run the `build.bat` file. It will output the exe to the dist folder.

## Image Development Guide

Configure a virtual machine with the vulnerabilities in place, and test to ensure that the scoring engine is working correctly.

When you have finished testing both the py and compiled exe, follow the below steps to create a quality image:
* Store the compiled exe and ico inside the Windows folder or any folder where clients won't look at normally, and possibly add hide attributes
* Create a shortcut for the exe and put it on the desktop
* Change the shortcut icon to the ico file
* Implement your own readme, and make sure to mention NOT TO DELETE SCORPIO
* Create a scheduled task or service to run Scorpio with highest privileges on log in
* Run it several times to test it out
* Delete any remnant files

## Known bugs

* Disabling a user will prevent the password changed check for that user
* Error messages display in the console after a sound is played by Scorpio

## Built With

* Python 3.11.4

## The Scorpio Team

* **Clement Chan** Scorpio Engine Developer - [slyq](https://github.com/slyq)
* **Jimmy Li** Scorpio Configuration Editor Developer - [jimmyl02](https://github.com/jimmyl02)
