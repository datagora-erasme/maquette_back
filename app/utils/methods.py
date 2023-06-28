import os
import hashlib
import base64
import datetime
import csv
from pprint import pprint
from random import choice, randint

from base64 import *
from os import environ

from app.utils.constants import *
import re

# Add your methods here


def get_environment():
    return environ.get("APPLICATION_ENV") or "development"


def escapeForDBFilter(string):
    return re.sub("[^0-9a-zA-Z_-]", "_", string).lower()


def isDevEnv():
    return environ.get("APPLICATION_ENV") == "development"


def generateCodeWith0(id, max="000"):
    if id < 10 and max == "000":
        return "000" + str(id)
    elif id < 100:
        return "00" + str(id)
    elif id < 1000:
        return "0" + str(id)
    else:
        return str(id)


def getXlsxCellsFormat(workbook, color=None, center=False):
    if color is None:
        color = "#FFD468"

    # style
    header_cell_format = workbook.add_format({"bold": True})
    header_cell_format.set_text_wrap()
    header_cell_format.set_border(1)
    header_cell_format.set_border_color("black")
    header_cell_format.set_bg_color(color)
    header_cell_format.set_align("vcenter")
    if center:
        header_cell_format.set_align("center")

    header_italic_cell_format = workbook.add_format({"italic": True})
    header_italic_cell_format.set_text_wrap()
    header_italic_cell_format.set_border(1)
    header_italic_cell_format.set_border_color("black")
    header_italic_cell_format.set_bg_color(color)
    header_italic_cell_format.set_align("vcenter")

    default_cell_format = workbook.add_format({})
    default_cell_format.set_text_wrap()
    default_cell_format.set_border(1)
    default_cell_format.set_border_color("black")
    default_cell_format.set_align("vcenter")

    bold_cell_format = workbook.add_format({"bold": True})
    bold_cell_format.set_text_wrap()
    bold_cell_format.set_align("vcenter")

    red_cell_format = workbook.add_format({})
    red_cell_format.set_text_wrap()
    red_cell_format.set_border(1)
    red_cell_format.set_border_color("black")
    red_cell_format.set_align("vcenter")
    red_cell_format.set_font_color("red")

    total_cell_format = workbook.add_format({"bold": True})
    total_cell_format.set_align("vcenter")
    total_cell_format.set_border(1)
    total_cell_format.set_border_color("black")
    total_cell_format.set_bg_color(color)

    # type
    currency_cell_format = workbook.add_format({"num_format": "#,##0.00 €"})
    currency_cell_format.set_border(1)
    currency_cell_format.set_border_color("black")
    currency_cell_format.set_align("vcenter")

    date_cell_format = workbook.add_format({"num_format": "dd/mm/yyyy"})
    date_cell_format.set_border(1)
    date_cell_format.set_border_color("black")
    date_cell_format.set_align("vcenter")

    percent_cell_format = workbook.add_format({"num_format": "#,## %"})
    percent_cell_format.set_border(1)
    percent_cell_format.set_border_color("black")
    percent_cell_format.set_align("vcenter")

    return {
        "default_cell_format": default_cell_format,
        "bold_cell_format": bold_cell_format,
        "red_cell_format": red_cell_format,
        "header_cell_format": header_cell_format,
        "header_italic_cell_format": header_italic_cell_format,
        "total_cell_format": total_cell_format,
        "currency_cell_format": currency_cell_format,
        "date_cell_format": date_cell_format,
        "percent_cell_format": percent_cell_format,
    }


# Base64 methods


def encodeB64(strToEncode):
    return base64.b64encode(strToEncode).decode()


def decodeB64(strToDecode):
    return base64.b64decode(strToDecode)


def exportFileToBase64(path_file):
    with open(path_file, "rb") as file:
        file_read = file.read()
        data = base64.b64encode(file_read)


# Crypto methods


def generateSalt(length=None):
    if length:
        return os.urandom(length)
    else:
        return os.urandom(32)


def hashString(strToHash, salt):
    # Type, strToHash (converted in UTF8), salt, iterations
    key = hashlib.pbkdf2_hmac("sha256", str(strToHash).encode("utf-8"), salt, 100000)

    saltedKey = salt + key
    return saltedKey


def hashStringWithSalt(strToHash, salt=None, lengthSalt=None):
    key = None

    # Generate Salt
    if not salt:
        salt = generateSalt(lengthSalt)
    # Generate Key
    key = hashString(str(strToHash).encode("utf-8"), salt)

    saltedKey = salt + key
    return saltedKey


def hashStringWithSaltB64(strToHash, salt=None, lengthSalt=None):
    # Generate SaltedKey
    saltedKey = hashStringWithSalt(strToHash, salt, lengthSalt)

    # Encode B64
    saltedB64 = encodeB64(saltedKey)
    return saltedB64


# methods for dates


def convertToFrString(string):
    if isinstance(string, datetime.datetime):
        return string.strftime("%d/%m/%Y à %Hh%M")
    elif isinstance(string, datetime.date):
        return string.strftime("%d/%m/%Y")
    else:
        dateTime = string.split(" ")
        if len(dateTime) == 2:
            dateValue = dateTime[0].split("-")
            timeValue = dateTime[1].split(":")
            return (
                dateValue[2]
                + "/"
                + dateValue[1]
                + "/"
                + dateValue[0]
                + " à "
                + timeValue[0]
                + "h"
                + timeValue[1]
            )
        else:
            dateValue = dateTime[0].split("-")
            return dateValue[2] + "/" + dateValue[1] + "/" + dateValue[0]


def convertToString(string):
    if isinstance(string, datetime.datetime):
        return string.__str__()
    elif isinstance(string, datetime.date):
        return string.__str__()
    else:
        dateTime = string.split(" ")
        if len(dateTime) == 2:
            dateValue = dateTime[0].split("-")
            timeValue = dateTime[1].split(":")
            return (
                dateValue[2]
                + "/"
                + dateValue[1]
                + "/"
                + dateValue[0]
                + " à "
                + timeValue[0]
                + "h"
                + timeValue[1]
            )
        else:
            dateValue = dateTime[0].split("-")
            return dateValue[2] + "/" + dateValue[1] + "/" + dateValue[0]


def generateCsvFromDatas(nameFile="test.csv", datasTable=[]):
    path_file = environ.get("PATH_GENERATED_FILES") + "csv/" + nameFile
    headers = datasTable[0].keys()

    try:
        with open(path_file, "w+", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for data in datasTable:
                writer.writerow(data)

    except Exception as error:
        print("Error while writing the CSV file", error)
        return False

    return True


def debogClass(aClass):
    pprint(vars(aClass))


def pwdGenerator(n, min=True, maj=True, chif=True, cs=True):
    # lists for pwd generation
    alphabet_min = [chr(i) for i in range(97, 123)]
    alphabet_maj = [chr(i) for i in range(65, 91)]
    chiffres = [chr(i) for i in range(48, 58)]
    caracteres_speciaux = [
        "%",
        "_",
        "-",
        "!",
        "$",
        "^",
        "&",
        "#",
        "(",
        ")",
        "[",
        "]",
        "=",
        "@",
    ]

    alphabets = dict()
    key = 0
    if min:
        alphabets[key] = alphabet_min
        key += 1
    if maj:
        alphabets[key] = alphabet_maj
        key += 1
    if chif:
        alphabets[key] = chiffres
        key += 1
    if cs:
        alphabets[key] = caracteres_speciaux
        key += 1

    mdp = ""
    for i in range(n):
        s = randint(0, key - 1)
        mdp += choice(alphabets[s])

    return mdp
