from app import infoLogger, errorLogger
from os import environ
from flask import Blueprint, current_app, jsonify, request, send_file
from werkzeug.local import LocalProxy
from nltk import ngrams
import base64
import binascii
import pyvista as pv
import numpy as np
import pymeshfix

# Utils import
from app.utils.methods import *
from app.utils.constants import *

# Create Blueprint & get logger
dataprocess = Blueprint("dataprocess", __name__)
logger = LocalProxy(lambda: current_app.logger)


def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return jsonify({"msg": "Data isn't Base64"}), 500


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
        decoded = base64.b64decode(base64toDecode).decode("utf-8")
        encoded = base64.b64encode(bytes(decoded, encoding="utf-8"))
        if base64toDecode == str(encoded, encoding="utf-8"):
            new_file = open("tempstl.stl", "w")
            new_file.write(decoded)
            new_file.close()

            p = pv.Plotter()

            mesh_tofix = pv.read("tempstl.stl")
            mesh = mesh_tofix.fill_holes(1000, inplace=True)

            fixer = pymeshfix.MeshFix(mesh)

            voxels = pv.voxelize(
                fixer.mesh.triangulate(),
                density=fixer.mesh.length / 180,
                check_surface=False,
            ).connectivity()
            p.add_mesh(voxels, color=True, show_edges=True, opacity=1)

            p.enable_anti_aliasing("ssaa")
            p.export_obj("voxeled.obj")
            os.remove("tempstl.stl")
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
