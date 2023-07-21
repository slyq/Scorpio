import env
import ast
import base64

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


def extractconf(scoringEnginePath):
    with open(f'C:/{scoringEnginePath}/conf.txt', 'r') as f:
        cipherconf = f.read().replace('\n', '')
    confstr = decrypt(cipherconf, env.KEY)
    conflist = ast.literal_eval(base64.b64decode(confstr).decode("utf-8"))
    USER = conflist["mainUser"]
    IMAGE_NAME = conflist["name"]
    return conflist, USER, IMAGE_NAME