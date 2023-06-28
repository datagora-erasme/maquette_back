from flask.helpers import make_response
from app import infoLogger, errorLogger
from os import environ, name
from flask import Blueprint, current_app, jsonify, request, render_template
import csv
import pdfkit

# Utils import
from app.utils.methods import *
from app.utils.generatePdf import *

# Create Blueprint & get logger
core = Blueprint("core", __name__)


@core.before_request
def before_request_func():
    current_app.logger.name = "core"


# Add status to app


@core.route("/status", methods=["GET"])
def status():
    return jsonify({"msg": "Running!"}), 200


@core.route("/test", methods=["GET"])
def test():
    infoLogger.info("test route hit")

    return jsonify({"msg": "Test OK !"}), 200


@core.route("/generate-csv", methods=["GET"])
def testGenerateCsv():
    infoLogger.info(request.path)

    listUsers = [
        {
            "id": 1,
            "firstname": "John",
            "lastname": "Doe",
            "email": "jdoe@unknown.com",
            "phone": None,
        },
        {
            "id": 2,
            "firstname": "Toto",
            "lastname": "Tutu",
            "email": "totutotu@test.fr",
            "phone": "0656553133",
        },
        {
            "id": 3,
            "firstname": "Jean-Pierre",
            "lastname": "Pallnort",
            "email": "jpp@free.fr",
            "phone": None,
        },
        {
            "id": 4,
            "firstname": "Tom",
            "lastname": "Sawyer",
            "email": "tomtom@amis.fr",
            "phone": None,
        },
    ]

    nameFile = "test_users.csv"
    infoLogger.info("try to create csv file " + nameFile)

    if generateCsvFromDatas(nameFile, listUsers):
        return jsonify({"msg": "File generated successfuly"}), 200
    else:
        errorLogger.error({"msg": "Error during creation of CSV file " + nameFile})
        return jsonify({"msg": "Error during creation of CSV file"}), 500


@core.route("/generate-pdf", methods=["GET"])
def testGeneratePdf():
    infoLogger.info(request.path)

    datasTable = (
        [
            {
                "id": 1,
                "firstname": "John",
                "lastname": "Doe",
                "email": "jdoe@unknown.com",
                "phone": None,
            },
            {
                "id": 2,
                "firstname": "Toto",
                "lastname": "Tutu",
                "email": "totutotu@test.fr",
                "phone": "0656553133",
            },
            {
                "id": 3,
                "firstname": "Jean-Pierre",
                "lastname": "Pallnort",
                "email": "jpp@free.fr",
                "phone": None,
            },
            {
                "id": 4,
                "firstname": "Tom",
                "lastname": "Sawyer",
                "email": "tomtom@amis.fr",
                "phone": None,
            },
        ],
    )

    datas = {
        "datasTable": datasTable,
        "headersDatasTable": datasTable[0].keys(),
        "sender": {
            "name": "Xavier Thiermant",
            "address": "404 route inconnue",
            "tel": None,
        },
        "target": {"name": "Toto Pierce", "email": "toto@pierce.fr"},
        "date_send": datetime.datetime(2021, 4, 30).strftime("%D/%m/%Y"),
        "title": "Test generate pdf",
    }
    nameFile = "test_users.pdf"

    newPdf = generatePdf("content_table.html", nameFile, datas)
    if newPdf.createPdf():
        return jsonify({"msg": "File generated successfuly"}), 200
    else:
        return (
            jsonify(
                {"status": "error", "msg": "Error during creation of the PDF file"}
            ),
            500,
        )
