import os
import sys
import getpass
import win32net
import win32security
import win32service
import win32net
from pathlib import Path
import pywintypes
import subprocess
import winerror
import winreg
import winsound
from time import gmtime, strftime, sleep, ctime
from datetime import datetime, date, timedelta
import requests
import json
import hashlib
import base64
import ast
import random
import string
from urllib.parse import quote

# from dotenv import load_dotenv
# extDataDir = os.getcwd()
# if getattr(sys, 'frozen', False):
#     extDataDir = sys._MEIPASS
# print(os.path.join(extDataDir, '.env'))
# load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))
import env

try:
    TTKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
    TT = winreg.QueryValueEx(TTKey, "TT")[0]
except:
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio')
    TTKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0,
                           (winreg.KEY_WOW64_64KEY + winreg.KEY_WRITE))
    TT = str(datetime.utcnow())
    winreg.SetValueEx(TTKey, "TT", 0, winreg.REG_SZ, TT)
    winreg.CloseKey(TTKey)

wait = input("""While competing in Troy Cyber:
I will consider the ethical and legal implications of all my actions. I will not conduct, nor will I condone, any actions that attack, hack, penetrate, or interfere with another team’s or individual’s computer system, the competition server, or the scoring engine.
I will not keep or download any instances of competition images outside of their specified dates of use
I will comply with ethical rules and all statements mentioned above.
[Y/N]""")
if wait not in ['Y', 'y', 'Yes', 'yes', 'YES']:
    exit()

# DEFINE THESE VARIABLES #
USER = ""
SCORING_FOLDER = "Scoring Engine"  # format: C:/[path]
IMAGE_NAME = ""
IMAGE_BIT = 64  # 32/64 # DOUBLE CHECK ME
IMAGERS = "Scorpio"
REFRESH_RATE = 30
IS_AD = False
IS_GUI = True
##########################

FLAGS = []
uploadStatus = "<span style=\"color:green\">OK</span>"


def sendScore(totalPoints, time):
    time = [x for x in time.split(":")][:2]
    if time[0][0] == '0' and len(time[0]) == 2:
        time[0] = time[0][1]
    body = {"name": NAME, "imageName": IMAGE_NAME, "score": totalPoints, "totalTime": ":".join(time)}
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
        pass


try:
    IDKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
    ID = winreg.QueryValueEx(IDKey, "ID")[0]
    if len(ID) != 6:
        raise ValueError("Who touched a my reg!")
except:
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio')
    IDKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Scorpio', 0,
                           (winreg.KEY_WOW64_64KEY + winreg.KEY_WRITE))
    ID = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
    winreg.SetValueEx(IDKey, "ID", 0, winreg.REG_SZ, ID)
    winreg.CloseKey(IDKey)
NAME = hashlib.sha256(ID.encode("UTF-8")).hexdigest()[:6]

print("\nYour unique ID on the scoreboard is " + NAME + "\n")


def isuppercase(c):
    return 65 <= ord(c) <= 90


def islowercase(c):
    return 97 <= ord(c) <= 122


def isletter(c):
    return isuppercase(c) or islowercase(c)


def filteredkey(key):
    result = []
    for i in range(0, len(key)):
        c = key[i]
        if isletter(c):
            result.append((ord(c) - 65) % 32)
    return result


def decrypt(encryptedtext, key):
    filtered = filteredkey(key)
    outputkey = []
    for i in range(0, len(filtered)):
        outputkey.append((26 - filtered[i]) % 26)
    output = ""
    j = 0
    for i in range(0, len(encryptedtext)):
        c = encryptedtext[i]
        if isuppercase(c):
            output += chr((ord(c) - 65 + outputkey[j % len(outputkey)]) % 26 + 65)
            j += 1
        elif islowercase(c):
            output += chr((ord(c) - 97 + outputkey[j % len(outputkey)]) % 26 + 97)
            j += 1
        else:
            output += c
    return output


def extractconf():
    global conflist
    global USER
    global IMAGE_NAME
    with open('C:/Scoring Engine/conf.txt', 'r') as f:
        cipherconf = f.read().replace('\n', '')
    confstr = decrypt(cipherconf, env.KEY)
    conflist = ast.literal_eval(base64.b64decode(confstr).decode("utf-8"))
    USER = conflist["mainUser"]
    IMAGE_NAME = conflist["name"]

extractconf()

STARTTIME = datetime.utcnow()
UPDATETIME = datetime.utcnow()
TOTALTIME = timedelta(0, 0, 0)
warning = ""

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
    <title>""" + IMAGE_NAME + """ Scoring Report</title>
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
            <h3 class="center">Current Team ID: <span style="color:green">""" + NAME + """</span></h3>
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
        self.penalty = pcp[2]
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
                for l in content:
                    if "ANSWER:" in l:
                        answerlines.append(l)
                answers = answerlines[4:]
                ans = ""
                for answer in answers:
                    ans += answer.split("ANSWER: ")[1] + "[/n]"
                ans = ans[:-4]
                possible = self.answer.split("[/;]")
                if ans in possible:
                    return 1, self.points, self.comment, self.penalty
            return 0, self.points, self.comment, self.penalty
        except:
            return 3, self.points, self.comment, "Error in checking file"


class User(Vulnerability):
    userID = 0
    conf = -1

    username = ""
    password = ""  # PREVIOUS PASSWORD CANNOT BE BLANK FOR THIS TO WORK (possible secpol error)
    exist = None
    changePw = None  # you cannot check the password of a disabled user (class will reenable)
    changeName = None  # if checking changeName, username cannot be userID
    oldName = ""

    groupname = ""
    authorized = None

    def add(self, ext):
        if ext[0] == "User":
            self.conf = 0
            self.username = ext[1]  # prefer it to be user ID number
            self.password = ext[2]
            self.exist = ext[3]
            self.changePw = ext[4]
            self.changeName = ext[5]
            self.oldName = ext[6]
            self.pwExpires = ext[7]
        elif ext[0] == "Group":
            self.conf = 1
            self.username = ext[1]
            self.groupname = ext[2]
            self.authorized = ext[3]
        else:
            print("Error in ext[0] of " + self.comment)

    def check(self):
        try:  # if given an ID (number) instead, convert
            if self.changeName is not None:
                if self.userID == 0:
                    self.userID = int(self.username)
                for user in userList:
                    if user['user_id'] == self.userID:  # if matching ID
                        if (user['name'] != self.oldName) == self.changeName:  # if nonmatching names
                            return 1, self.points, self.comment, self.penalty  # changed name
                        return 0, self.points, self.comment, self.penalty  # not changed name
                return 3, self.points, self.comment, "User wasn't found"  # invalid ID for vuln
            else:
                if self.userID == 0:
                    self.userID = int(self.username)  # convert "username" (a number) into the user ID number
                for user in userList:
                    if user['user_id'] == self.userID:  # found matching ID
                        self.username = user['name']  # username changed to actual name
        except:  # in self case the username is a string to begin with, continue on
            pass
        if self.conf == 0:  # User
            if self.exist is not None:  # if not properly initiated exist value
                if self.exist:  # if user should exist
                    if self.username in usernameList:  # if user does exist
                        if self.changePw:
                            try:  # test if can login successfully with old password
                                hUser = win32security.LogonUser(
                                    self.username,
                                    None,
                                    self.password,
                                    win32security.LOGON32_LOGON_NETWORK,
                                    win32security.LOGON32_PROVIDER_DEFAULT
                                )
                                return 0, self.points, self.comment, self.penalty
                            except win32security.error as e:
                                # winerror values: 1326 is can't login, 1385 is login perm denied, 1907 is passwd must change, 1909 is locked out
                                # priority of errors (high to low): 1385, 1326, 1907 (idk where 1909 goes)
                                # so if error is 1326, user is already enabled
                                if e.winerror == 1326:
                                    return 1, self.points, self.comment, self.penalty
                                if e.winerror == 1909:
                                    devnull = open(os.devnull, 'w')
                                    try:
                                        subprocess.call("net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" /active:yes", shell=True,
                                                        startupinfo=None, stdout=devnull)
                                    except Exception as e:
                                        return 3, self.points, self.comment, e
                                    try:
                                        hUser = win32security.LogonUser(
                                            self.username,
                                            None,
                                            self.password,
                                            win32security.LOGON32_LOGON_NETWORK,
                                            win32security.LOGON32_PROVIDER_DEFAULT
                                        )
                                        return 0, self.points, self.comment, self.penalty
                                    except:
                                        return 1, self.points, self.comment, self.penalty
                                else:
                                    return 0, self.points, self.comment, self.penalty
                            except Exception as e:
                                return 3, self.points, self.comment, e
                        else:  # if you don't care about password change
                            if self.pwExpires:
                                try:
                                    result = subprocess.check_output(
                                        "wmic useraccount | find /I \"" + self.username + "\"", shell=True,
                                        startupinfo=None).decode('utf-8')
                                    active = result.split()[9]
                                    if active == "FALSE":
                                        return 0, self.points, self.comment, self.penalty  # user password doesn't expire
                                    return 1, self.points, self.comment, self.penalty  # user password does expire
                                except Exception as e:
                                    pass
                            else:
                                try:
                                    result = subprocess.check_output(
                                        "net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"Account Active\"", shell=True,
                                        startupinfo=None).decode('utf-8')
                                    active = result.split()[2]
                                    if active == "No":
                                        return 0, self.points, self.comment, self.penalty  # user is disabled
                                    return 1, self.points, self.comment, self.penalty  # user is enabled
                                except Exception as e:
                                    pass
                    return 2, self.points, self.comment, self.penalty  # penalty for having deleted user
                else:  # if user shouldn't exist, if match found return
                    if self.username in usernameList:
                        try:
                            result = subprocess.check_output(
                                "net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"Account Active\"", shell=True,
                                startupinfo=None).decode('utf-8')
                            active = result.split()[2]
                            if active == "No":  # if user is disabled instead of deleted
                                return 1, self.points, self.comment, self.penalty  # user is disabled
                            return 0, self.points, self.comment, self.penalty  # user is neither disabled nor deleted
                        except Exception as e:
                            pass
                    return 1, self.points, self.comment, self.penalty  # user is deleted
            else:
                return 3, self.points, self.comment, "Exist value was set to None, needs to be set to True or False"
        elif self.conf == 1:  # Group
            if self.authorized is not None:
                if self.username != "":
                    if self.username in usernameList:
                        try:
                            result = subprocess.check_output("net user " + ("/domain " if IS_AD else "") + "\"" + self.username + "\" | find /I \"*\"",
                                                             shell=True, startupinfo=None).decode('utf-8')
                            groups = [x.strip() for x in
                                      result.split("*")[1:]]  # groups = the groups that username is in
                            for x in range(0, len(groups)):
                                if "Global Group memberships" in groups[x]:
                                    groups[x] = groups[x].split()[0]
                            if self.authorized:  # if user is authorized in group
                                if self.groupname in groups:  # in group
                                    return 1, self.points, self.comment, self.penalty
                                else:  # not in group
                                    return 0, self.points, self.comment, self.penalty
                            else:  # if user isn't authorized in group
                                if self.groupname in groups:  # in group
                                    return 0, self.points, self.comment, self.penalty
                                else:  # not in group
                                    return 1, self.points, self.comment, self.penalty
                        except Exception as e:
                            return 3, self.points, self.comment, e
                    if not self.authorized:
                        return 1, self.points, self.comment, self.penalty
                    return 0, self.points, self.comment, self.penalty  # user doesn't exist in the first place, penalty will be somewhere else
                else:
                    try:
                        result = subprocess.check_output("net localgroup | find /I \"" + self.groupname + "\"",
                                                         shell=True, startupinfo=None).decode('utf-8')
                        if "*" + self.groupname in result.split() == self.authorized:
                            return 1, self.points, self.comment, self.penalty
                        if IS_AD:
                            result = subprocess.check_output("net group | find /I \"" + self.groupname + "\"",
                                                             shell=True, startupinfo=None).decode('utf-8')
                            if "*" + self.groupname in result.split() == self.authorized:
                                return 1, self.points, self.comment, self.penalty
                        return 0, self.points, self.comment, self.penalty
                    except Exception as e:
                        if not self.authorized:
                            return 1, self.points, self.comment, self.penalty
                        return 3, self.points, self.comment, e
            else:
                return 3, self.points, self.comment, "Authorized value was set to None, needs to be set to True or False"


class Policy(Vulnerability):
    valid = None
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
                for line in secEdit.read().replace("\0", "").split("\n"):
                    if self.policy in line:
                        if "\\" in self.policy:  # reg-based policy
                            self.myValue = line.split(",")[1].strip('\"')
                        else:  # non-reg-based policy
                            self.myValue = line.split()[2].strip('\"')
                        # print("myValue: " + str(self.myValue) + " " + self.scoreOn + "; value: " + str(self.value))
                        if self.scoreOn == ">":
                            self.valid = int(self.myValue) > self.value
                        elif self.scoreOn == "<":
                            self.valid = int(self.myValue) < self.value
                        elif self.scoreOn == ">=":
                            self.valid = int(self.myValue) >= self.value
                        elif self.scoreOn == "<=":
                            self.valid = int(self.myValue) <= self.value
                        elif self.scoreOn == "=":
                            self.valid = int(self.myValue) == self.value
                        elif self.scoreOn == "!=":
                            self.valid = int(self.myValue) != self.value
                        elif self.scoreOn == "contain":
                            self.valid = self.value in self.myValue
                        elif self.scoreOn == "!contain":
                            self.valid = self.value not in self.myValue
                        elif self.scoreOn == "line":
                            self.valid = True
                        else:
                            return 3, self.points, self.comment, self.penalty  # invalid scoreOn
                if self.scoreOn == "!line" and self.valid is None:
                    return 1, self.points, self.comment, self.penalty
                elif self.scoreOn == "!line":
                    return 0, self.points, self.comment, self.penalty
                elif self.valid:
                    return 1, self.points, self.comment, self.penalty
                elif not self.valid:
                    return 0, self.points, self.comment, self.penalty
                else:
                    return 3, self.points, self.comment, "Couldn't find policy"
        except Exception as e:
            return 3, self.points, self.comment, e


class Command(Vulnerability):
    cmdOutput = ""  # for own class use

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
                    return 1, self.points, self.comment, self.penalty
                else:
                    return 0, self.points, self.comment, self.penalty
            except Exception as e:
                if self.output == "ERROR" and self.expected:
                    return 1, self.points, self.comment, self.penalty
                return 3, self.points, self.comment, e
        else:
            return 3, self.points, self.comment, "Expected value was set to None, needs to be set to True or False"


class Reg(Vulnerability):
    valid = None

    path = ''
    key = None
    index = 0
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
                if IMAGE_BIT == 32:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0,
                                         (winreg.KEY_WOW64_32KEY + winreg.KEY_READ))
                else:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0,
                                         (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
            if self.hkey == "HKLM":
                if IMAGE_BIT == 32:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.path, 0,
                                         (winreg.KEY_WOW64_32KEY + winreg.KEY_READ))
                else:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.path, 0,
                                         (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
            if self.hkey == "HKU":
                if IMAGE_BIT == 32:
                    key = winreg.OpenKey(winreg.HKEY_USERS, self.path, 0, (winreg.KEY_WOW64_32KEY + winreg.KEY_READ))
                else:
                    key = winreg.OpenKey(winreg.HKEY_USERS, self.path, 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
            if self.scoreOn == "path":
                return 1, self.points, self.comment, self.penalty
            if self.scoreOn == "!path":
                return 0, self.points, self.comment, self.penalty
            keyVal = winreg.QueryValueEx(key, self.key)
            # handling of REG_BINARY cases (represented in hex)
            try:
                keyVal = ord(keyVal[0].decode()[self.index])
                if not isinstance(self.value, int):
                    self.value = int(self.value, 16)
                # print("value at byte " + str(self.index) + " of key " + self.key + " in path " + self.path + " has decimal value of " + str(keyVal) + " (hex is " + str(hex(keyVal)) + "), scoring if it is " + self.scoreOn + " " + str(self.value) + " (hex is " + str(hex(self.value)) + ")")
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
                return self.valid, self.points, self.comment, self.penalty
            except AttributeError:
                pass
            # handling of DWORD or STRING
            # print("value at index " + str(self.index) + " of key " + self.key + " in path " + self.path + " has value of " + str(keyVal) + ", scoring if it is " + self.scoreOn + " " + str(self.value))
            # print(keyVal[self.index])
            # print(self.value)
            # print(type(keyVal[self.index]))
            # print(type(self.value))
            # print(keyVal[self.index] == self.value)
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
            elif self.scoreOn == "exist":
                self.valid = True
            elif self.scoreOn == "!exist":
                self.valid = False
            if self.valid:
                return 1, self.points, self.comment, self.penalty
            elif not self.valid:
                return 0, self.points, self.comment, self.penalty
        except Exception as e:
            if self.scoreOn == "!exist" or self.scoreOn == "!path":
                return 1, self.points, self.comment, self.penalty
            if self.scoreOn == "path":
                return 0, self.points, self.comment, self.penalty
            return 3, self.points, self.comment, e


class Share(Vulnerability):
    name = ''  # if asking for new share creation, must include specified name
    path = ''  # must use \\, only required if checking for an authorized shared folder
    authorized = None
    defaultOnly = None  # checks if only default folders are present

    def add(self, ext):
        self.name = ext[0]
        self.path = ext[1]
        self.authorized = ext[2]
        self.defaultOnly = ext[3]

    def check(self):
        if self.defaultOnly:  # defaultOnly is priority
            if len(activeShares) == 6:
                defaultlist = ["ADMIN$", "C:\\Windows", "C$", "C:\\", "IPC$", ""]
                for x in range(0, 5):
                    if not defaultlist[x] == activeShares[x]:
                        return 0, self.points, self.comment, self.penalty
                return 1, self.points, self.comment, self.penalty
            return 0, self.points, self.comment, self.penalty
        if self.authorized is not None:
            try:
                if self.authorized:
                    if self.name in activeShares:
                        index = activeShares.index(self.name)
                        if activeShares[index + 1] == self.path:
                            return 1, self.points, self.comment, self.penalty
                    return 2, self.points, self.comment, self.penalty  # path is wrong, or folder doesn't exist
                else:
                    if self.name in activeShares:
                        return 0, self.points, self.comment, self.penalty
                    return 1, self.points, self.comment, self.penalty
            except Exception as e:
                return 3, self.points, self.comment, e
        else:
            return 3, self.points, self.comment, "Authorized setting was set to None, needs to be set to True or False"


class ServFeat(Vulnerability):
    conf = -1

    name = ""
    authorized = None

    def add(self, ext):
        if ext[0] == "Serv":
            self.conf = 0
        elif ext[0] == "Feat":
            self.conf = 1
        elif ext[0] == "DelServ":
            self.conf = 2
        self.name = ext[1]
        self.authorized = ext[2]

    def check(self):
        # For status: 4 = running, 1 = stopped
        # For startup: 2 = Auto-Start, 4 = Disabled, 3 = Demand-start
        if self.authorized is not None:
            if self.conf == 0:  # service
                try:
                    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                    type = win32service.SERVICE_WIN32
                    openService = win32service.OpenService(scm, self.name, win32service.SERVICE_ALL_ACCESS)
                    status = win32service.QueryServiceStatus(openService)
                    startup = win32service.QueryServiceConfig(openService)
                    if self.authorized == "Full":
                        if status[1] == 4 and startup[1] < 3:
                            return 1, self.points, self.comment, self.penalty
                        return 0, self.points, self.comment, self.penalty
                    elif self.authorized:
                        if startup[1] != 4:
                            return 1, self.points, self.comment, self.penalty
                        return 0, self.points, self.comment, self.penalty
                    else:
                        if status[1] == 1 and startup[1] == 4:
                            return 1, self.points, self.comment, self.penalty
                        return 0, self.points, self.comment, self.penalty
                except Exception as e:
                    return 3, self.points, self.comment, e
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
                            # print(self.name + " state is " + state + ", it's existance should be " + str(self.authorized))
                            if (
                                    state == "Disabled") != self.authorized:  # if state enabled and authorized, or state disabled and unauthorized
                                return 1, self.points, self.comment, self.penalty
                            return 0, self.points, self.comment, self.penalty
                    return 3, self.points, self.comment, "Feature name wasn't found"  # invalid feature name
                except Exception as e:
                    return 3, self.points, self.comment, e
            elif self.conf == 2:  # service in need of deletion/uninstallation, but not a feature
                try:
                    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                    type = win32service.SERVICE_WIN32
                    openService = win32service.OpenService(scm, self.name, win32service.SERVICE_ALL_ACCESS)
                    status = win32service.QueryServiceStatus(openService)
                    startup = win32service.QueryServiceConfig(openService)
                    return 0, self.points, self.comment, self.penalty
                except:
                    return 1, self.points, self.comment, self.penalty
            else:
                print("invalid conf on " + self.comment)
        else:
            return 3, self.points, self.comment, "Authorized setting was set to None, needs to be set to True or False"


class File(Vulnerability):
    path = ""
    authorized = None

    def add(self, ext):
        self.path = ext[0]
        self.authorized = ext[1]

    def check(self):
        if self.authorized is not None:
            try:
                if self.authorized and (
                        os.path.isfile(self.path) or os.path.isdir(self.path)):  # file is allowed and path exists
                    return 1, self.points, self.comment, self.penalty
                elif not (self.authorized or (os.path.isfile(self.path) or os.path.isdir(
                        self.path))):  # file isn't allowed and path doesn't exist
                    return 1, self.points, self.comment, self.penalty
                elif self.authorized:  # file is allowed and path doesn't exist
                    return 2, self.points, self.comment, self.penalty  # penalty for deleting critical file
                else:  # file isn't allowed and path still exists
                    return 0, self.points, self.comment, self.penalty
            except Exception as e:
                return 3, self.points, self.comment, e
        else:
            return 3, self.points, self.comment, "Authorized set to None, needs to be True or False"


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
                    if self.name in installedPrograms:
                        return 1, self.points, self.comment, self.penalty
                    elif "C:" in self.path and Path(self.path).exists():
                        return 1, self.points, self.comment, self.penalty
                    return 0, self.points, self.comment, self.penalty  # possible penalty for uninstalling critical service
                else:
                    if not Path(self.path).exists():
                        return 1, self.points, self.comment, self.penalty
                    return 0, self.points, self.comment, self.penalty  # program still installed when it should be gone
            except Exception as e:
                return 3, self.points, self.comment, e
        else:
            return 3, self.points, self.comment, "Authorized setting was set to None, needs to be set to True or False"


'''END OF CLASSES---------------------------------------------------------------------------------------------------'''


def getMax():
    global maxPoints
    for vuln in vulns:
        maxPoints += int(vuln.points)


def runScoring():
    global lastPoints
    global TOTALTIME
    vulnLines = []
    penalLines = []
    totalPoints = 0
    gainPoints = 0
    losePoints = 0
    currentVulns = 0
    currentPenal = 0
    for vuln in vulns:
        foo = vuln.check()
        if int(foo[0]) == 1 and int(foo[1]) > 0:
            totalPoints += int(foo[1])
            gainPoints += int(foo[1])
            currentVulns += 1
            vulnLines.append(str(foo[2]) + " - " + str(foo[1]) + " pts" + ("<br>" if IS_GUI else "") + "\n")
    for penal in penals:
        bar = penal.check()
        if int(bar[0]) == 0 or int(bar[0]) == 2:
            totalPoints -= -1*int(bar[1])
            losePoints += -1*int(bar[1])
            currentPenal += 1
            penalLines.append(str(bar[3]) + " - " + str(-1*int(bar[1])) + " pts" + ("<br>" if IS_GUI else "") + "\n")
    try:
        req = requests.get(env.SCORING_SERVER + "/getScores?name=" + quote(NAME) + "&imageName=" + IMAGE_NAME)
        UPDATETIME = datetime.strptime(ast.literal_eval(req.content.decode("utf-8"))[0]["updateTime"],
                                       '%Y-%m-%dT%H:%M:%S.%fZ')
        TOTALTIME = UPDATETIME - STARTTIME
        if [int(float(x)) for x in str(TOTALTIME).split(":")] > [6, 0, 0]:
            warning = """<h3 class="center"><span style="color:yellow">Warning: time period exceeded</span></h3>"""
    except Exception as e:
        pass
    writeScores(IMAGE_NAME, vulnLines, penalLines, totalPoints, gainPoints, losePoints, currentVulns, currentPenal,
                len(vulns), strftime("%Y-%m-%d %H:%M:%S"), TOTALTIME)
    try:
        if totalPoints > lastPoints and IS_GUI:
            winsound.PlaySound("C:/" + SCORING_FOLDER + "/gain.wav", winsound.SND_FILENAME)
        elif totalPoints < lastPoints and IS_GUI:
            winsound.PlaySound("C:/" + SCORING_FOLDER + "/alarm.wav", winsound.SND_FILENAME)
    except:
        pass
    lastPoints = totalPoints


def writeScores(imageName, vulnLines, penalLines, totalPoints, gainPoints, losePoints, currentVulns, currentPenal,
                totalVulns, time, timeElapsed):
    sendScore(totalPoints, formatTime(timeElapsed))
    with open("C:/Scoring Engine/Scoring Report." + ("html" if IS_GUI else "txt"), 'w') as output_file:
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
                newLine = newLine.replace("{{TIME}}", time)
                newLine = newLine.replace("{{RUNTIME}}", formatTime(timeElapsed))
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
    try:
        level = 3
        resume = 0
        while True:
            localUserList, total, resume = win32net.NetUserEnum(None, level, 0, resume, 999999)
            for user in localUserList:
                userList.append(user)
                usernameList.append(user['name'])
            if resume == 0:
                break

    except pywintypes.error as e:
        print(e)


def exportPolicies():
    try:
        subprocess.check_output("SecEdit.exe /export /cfg \"C:\\" + SCORING_FOLDER + "\\securityExport.inf\"")
    except Exception as e:
        print(e)


def getShares():
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
        print(e)


def getInstalledPrograms():
    if IMAGE_BIT == 32:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', 0,
                         (winreg.KEY_WOW64_32KEY + winreg.KEY_READ))
    else:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', 0,
                         (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
    for i in range(winreg.QueryInfoKey(key)[0]):
        name = winreg.EnumKey(key, i)
        try:
            if IMAGE_BIT == 32:
                subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\' + name, 0,
                                    (winreg.KEY_WOW64_32KEY + winreg.KEY_READ))
            else:
                subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\' + name, 0,
                                    (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
            displayName = winreg.QueryValueEx(subkey, "DisplayName")[0]
            installedPrograms.append(displayName)
        except:
            pass


# Function to run all information helpers
def runInfo():
    getUsers()
    getInstalledPrograms()
    exportPolicies()
    getShares()


# END OF GATHER INFO SECTION------------------------------------------------------------------------------------------ #


'''DEFINE YOUR VULNS BELOW-------------------------------------------------------------------------------------------'''

extractconf()

def str2bool(arg):
    return arg.lower() in ("true", "1")

for forens in conflist["forensics"]:
    if int(forens["points"]) >= 0:
        vulns.append(Forensics([forens["filepath"], forens["answer"]], [forens["points"], forens["description"], ""]))
    else:
        penals.append(Forensics([forens["filepath"], forens["answer"]], [forens["points"], "", forens["description"]]))

for users in conflist["users"]:
    if users["option"] == "authorized" and users["argument"] == "True":
        if int(users["points"]) >= 0:
            vulns.append(User(["User", users["username"], None, True, None, None, "", None],
                              [users["points"], users["description"], ""]))
        else:
            penals.append(User(["User", users["username"], None, True, None, None, "", None],
                               [users["points"], "", users["description"]]))
    elif users["option"] == "authorized" and users["argument"] == "False":
        if int(users["points"]) >= 0:
            vulns.append(User(["User", users["username"], None, False, None, None, "", None],
                          [users["points"], users["description"], ""]))
        else:
            penals.append(User(["User", users["username"], None, False, None, None, "", None],
                              [users["points"], "", users["description"]]))
    elif users["option"] == "passwd":
        if int(users["points"]) >= 0:
            vulns.append(User(["User", users["username"], users["argument"], True, True, None, "", None],
                          [users["points"], users["description"], ""]))
        else:
            penals.append(User(["User", users["username"], users["argument"], True, True, None, "", None],
                              [users["points"], "", users["description"]]))
    elif users["option"] == "chname":
        if int(users["points"]) >= 0:
            vulns.append(User(["User", users["username"], None, True, None, True, users["argument"], None],
                          [users["points"], users["description"], ""]))
        else:
            penals.append(User(["User", users["username"], None, True, None, True, users["argument"], None],
                              [users["points"], "", users["description"]]))
    elif users["option"] == "pwexp":
        if int(users["points"]) >= 0:
            vulns.append(User(["User", users["username"], None, True, None, None, "", True],
                          [users["points"], users["description"], ""]))
        else:
            penals.append(User(["User", users["username"], None, True, None, None, "", True],
                              [users["points"], "", users["description"]]))
    else:
        print("Invalid options/arguments for users vulns")

for groups in conflist["groups"]:
    if int(groups["points"]) >= 0:
        vulns.append(User(["Group", groups["username"], groups["groupName"], str2bool(groups["shouldBeMember"])], [groups["points"], groups["description"], ""]))
    else:
        penals.append(User(["Group", groups["username"], groups["groupName"], str2bool(groups["shouldBeMember"])],
                          [groups["points"], "", groups["description"]]))

for pols in conflist["localpolicy"]:
    try:
        expectedValue = int(pols["expectedValue"])
        if int(pols["points"]) >= 0:
            vulns.append(Policy([pols["policyName"], pols["condition"], expectedValue], [pols["points"], pols["description"], ""]))
        else:
            penals.append(Policy([pols["policyName"], pols["condition"], expectedValue],
                                [pols["points"], "", pols["description"]]))
    except:
        if int(pols["points"]) >= 0:
            vulns.append(Policy([pols["policyName"], pols["condition"], pols["expectedValue"]], [pols["points"], pols["description"], ""]))
        else:
            penals.append(Policy([pols["policyName"], pols["condition"], pols["expectedValue"]],
                                [pols["points"], "", pols["description"]]))

for comms in conflist["commands"]:
    if int(comms["points"]) >= 0:
        vulns.append(Command([comms["command"], comms["splitPosition"], comms["comparisonValue"], str2bool(comms["matchOrNot"])], [comms["points"], comms["description"], ""]))
    else:
        penals.append(
            Command([comms["command"], comms["splitPosition"], comms["comparisonValue"], str2bool(comms["matchOrNot"])],
                    [comms["points"], "", comms["description"]]))

for featservs in conflist["featuresAndServices"]:
    if int(featservs["points"]) >= 0:
        vulns.append(ServFeat([featservs["servOrFeat"], featservs["itemName"], str2bool(featservs["authorized"])], [featservs["points"], featservs["description"], ""]))
    else:
        penals.append(ServFeat([featservs["servOrFeat"], featservs["itemName"], str2bool(featservs["authorized"])],
                              [featservs["points"], "", featservs["description"]]))

for shares in conflist["shares"]:
    if int(shares["points"]) >= 0:
        vulns.append(Share([shares["shareName"], shares["sharePath"], str2bool(shares["authorized"]), False], [shares["points"], shares["description"], ""]))
    else:
        penals.append(Share([shares["shareName"], shares["sharePath"], str2bool(shares["authorized"]), False],
                           [shares["points"], "", shares["description"]]))

for files in conflist["files"]:
    if int(files["points"]) >= 0:
        vulns.append(File([files["filePath"], str2bool(files["authorized"])], [files["points"], files["description"], ""]))
    else:
        penals.append(
            File([files["filePath"], str2bool(files["authorized"])], [files["points"], "", files["description"]]))

for apps in conflist["programs"]:
    if int(apps["points"]) >= 0:
        vulns.append(Program([apps["programName"], apps["programPath"], str2bool(apps["authorized"])], [apps["points"], apps["description"], ""]))
    else:
        penals.append(Program([apps["programName"], apps["programPath"], str2bool(apps["authorized"])],
                             [apps["points"], "", apps["description"]]))

for regs in conflist["registry"]:
    try:
        expectedValue = int(regs["expectedValue"])
        if int(regs["points"]) >= 0:
            vulns.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], expectedValue], [regs["points"], regs["description"], ""]))
        else:
            penals.append(
                Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], expectedValue],
                    [regs["points"], "", regs["description"]]))
    except:
        if int(regs["points"]) >= 0:
            vulns.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"], regs["expectedValue"]], [regs["points"], regs["description"], ""]))
        else:
            penals.append(Reg([regs["hKey"], regs["path"], regs["key"], regs["checkingIndex"], regs["condition"],
                              regs["expectedValue"]], [regs["points"], "", regs["description"]]))


'''END OF VULNS------------------------------------------------------------------------------------------------------'''

# MAIN SEQUENCE
print(IMAGE_NAME + " provided by Troy High School Cyber Defense Club.\nUnauthorized access to this image is not "
                   "tolerated.\nCopyright " + u'\u00A9' + " 2020 Scorpio" + u'\u2122' + "\nClement Chan and Jimmy Li")

getMax()
while True:
    runInfo()
    runScoring()
    # Clear Lists
    userList.clear()
    usernameList.clear()
    installedPrograms.clear()
    activeShares.clear()
    sleep(REFRESH_RATE)
