![Scorpio logo](https://github.com/slyq/Scorpio/blob/main/scorpio.png)

# Scorpio

Scorpio is a client-side Windows scoring engine tool designed to score the security of Windows machines given predefined vulnerabilities to check for. It is meant to mock CyberPatriot image scoring, and it provides a clean output of the security issues that are fixed.

| :warning: DISCLAIMER                                                                                                                                                                  |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Scorpio is designed for educational purposes, not for competitions! Scoring happens offline, but that also means that with enough effort, vulnerabilities can be extracted. Use at your own risk! |

### Prerequisites

Install Python 3.11. You also need to use a Windows system.

Install the required Python modules:

```sh
pip install -r requirements.txt
```

## Modifying the Engine to Your Purposes

Don't forget to test the engine (run as admin) to see if it runs without errors.

Once you are done, use pyinstaller to build an executable and add an icon and obfuscation through pyarmor if you desire.

```sh
pyinstaller --onefile -i scorpio.ico scorpio.py
```

## Configuration Editor

The configuration tool for Scorpio has been migrated to an electron app. It can be downloaded [here](https://drive.google.com/file/d/1WGncgS5qvgRrWK09IVnO-MkPiYfeC9ao/view?usp=sharing). Simply paste the encrypted configuration into your `conf.txt` file.

## Running the tests

Use a pre-built image or build a new one to test the vulnerabilities to ensure that the scoring engine is scoring correctly. Pretend that you are the client/user for better results (they may think one thing whereas you think another). Ensure that clients/users cannot accidentally mess up the engine.

## Putting the stuff on your image

* Move the "Scoring Engine" folder to "C:\Scoring Engine"
* Store the compiled exe and ico inside the Windows folder or any folder where clients won't look at normally, and possibly add hide attributes
* Create a shortcut for the exe and put it on the desktop
* Change the shortcut icon to the ico file
* Implement your own readme, and make sure to mention NOT TO DELETE SCORPIO
* Implement the forensics questions
* Create a scheduled task or service to run Scorpio with highest privileges on log in
* Run it several times to test it out
* Delete any remnant files

## Known bugs

* Disabling a user will prevent the password changed check for that user
* Sometimes you may have to manually open the features box so that `dism` gets the list

## Built With

* Python 3.11.4

## The Scorpio Team

* **Clement Chan** Scorpio Engine Developer - [slyq](https://github.com/slyq)
* **Jimmy Li** Scorpio Configuration Editor Developer - [jimmyl02](https://github.com/jimmyl02)
