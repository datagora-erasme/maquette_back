from app import infoLogger, errorLogger
from os import environ
from flask import Blueprint, current_app, jsonify, request, send_file
from werkzeug.local import LocalProxy
from nltk import ngrams
import base64
import binascii
import pyvista as pv
import numpy as np
from sys import platform

# Utils import
from app.utils.methods import *
from app.utils.constants import *

# Create Blueprint & get logger
dataprocess = Blueprint("dataprocess", __name__)
logger = LocalProxy(lambda: current_app.logger)


def voxelize(tempfile):
    """
    func: to use binvox for voxelization.
        @tempfile: the temp file created from the received data.
    """
    if platform == "linux" or platform == "linux2":
        os.system("binvox -c -d 200 -t msh " + tempfile)
    elif platform == "win32":
        os.system("binvox.exe -c -d 200 -t msh " + tempfile)


@dataprocess.before_request
def before_request_func():
    current_app.logger.name = "dataprocess"


@dataprocess.route("/mesh", methods=["POST"])
def meshrecieve():
    """
    Recieving Mesh File
    ---
    tags:
      - Data Processing
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          properties:
            data:
              type: string
              description: email of the user account
    responses:
      200:
        description: Base64 Data Received Successfully
      400:
        description: Bad Request
      403:
        description: Forbidden
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    form = request.json

    if form["data"]:
        base64toDecode = form["data"]
        try:
            base64.b64decode(base64toDecode)
        except binascii.Error:
            errorLogger.error(request.path + " error ")
            return jsonify({"msg": "This isn't a Base64"}), 400

        # Checking if the received base64 data is real and not corrupted
        decoded = base64.b64decode(base64toDecode).decode("utf-8")
        encoded = base64.b64encode(bytes(decoded, encoding="utf-8"))

        if base64toDecode == str(encoded, encoding="utf-8"):
            # Adding the data to a temp file
            new_file = open("tempstl.obj", "w")
            new_file.write(decoded)
            new_file.close()

            # Voxelizing the tempfile that contains the mesh to voxelize
            voxelize("tempstl.obj")
            os.remove("tempstl.obj")

            p = pv.Plotter()

            themesh = pv.read("tempstl.msh")

            p.add_mesh(themesh, color=True, show_edges=True, opacity=1)

            # If we want to enable the anti aliasing
            # p.enable_anti_aliasing("ssaa")

            # If we want to preview the result
            # p.show()

            # Using Pyvista to export the voxelized version of the mesh
            p.export_obj("voxeled.obj")

            os.remove("tempstl.msh")

            # Sending the voxelized mesh version to the front for rendering and visualisation
            with open("voxeled.obj", "r") as file:
                data = file.read()
                coded = base64.b64encode(bytes(data, encoding="utf-8"))
                file.close()
                os.remove("voxeled.obj")
                os.remove("voxeled.mtl")
            return jsonify({"data": str(coded, encoding="utf-8")}), 200
    else:
        errorLogger.error(request.path + " error ")
        return jsonify({"msg": "Data is empty"}), 400
