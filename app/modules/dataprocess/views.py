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

# WFS imports

import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService
from shapely.geometry import box
import pyvista as pv
import trimesh


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


@dataprocess.route("/bbox", methods=["POST"])
def meshrecieve():
    """
    Recieving BoundingBox
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
            bbox:
              type: string
              description: the used bbox
            ratio:
              type: string
              description: the used ratio
    responses:
      200:
        description: Data Received Successfully
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
    p = pv.Plotter()
    url = "https://geoserver-planta.exo-dev.fr/geoserver/Metropole/ows?"

    wfs = WebFeatureService(url=url)

    layer_name = "Metropole:bati"

    if form["bbox"]:
        params = dict(
            service="WFS",
            version="1.0.0",
            request="GetFeature",
            typeName=layer_name,
            outputFormat="json",
            srsName="EPSG:2154",
            bbox=form["bbox"],
            startIndex=0,
        )

        wfs_request_url = Request("GET", url, params=params).prepare().url

        data = gpd.read_file(wfs_request_url)

        splited = form["bbox"].split(",")

        mask = box(splited[0], splited[1], splited[2], splited[3])
        gdfclip = data.clip(mask, keep_geom_type=True)
        info = []
        for index, row in gdfclip.iterrows():
            if row["geometry"].geom_type == "Polygon":
                zt = {
                    "strid": row["strid"],
                    "geometry": row["geometry"],
                    "hauteur": row["hauteur"],
                }
                info.append(zt)
            elif row["geometry"].geom_type == "MultiPolygon":
                for j in row["geometry"].geoms:
                    zt = {
                        "strid": row["strid"],
                        "geometry": j,
                        "hauteur": row["hauteur"],
                    }
                    info.append(zt)

        for i in info:
            if i["hauteur"]:
                m = trimesh.creation.extrude_polygon(i["geometry"], height=i["hauteur"])
                p.add_mesh(m, color="lightblue", opacity=1)

        p.export_obj("scene.obj")
        # Voxelizing the tempfile that contains the mesh to voxelize
        voxelize("scene.obj")
        os.remove("scene.obj")
        os.remove("scene.mtl")

        themesh = pv.read("scene.msh")

        p.add_mesh(themesh, color=True, show_edges=True, opacity=1)

        # If we want to enable the anti aliasing
        # p.enable_anti_aliasing("ssaa")

        # If we want to preview the result
        # p.show()

        # Using Pyvista to export the voxelized version of the mesh
        p.export_obj("voxeled.obj")

        os.remove("scene.msh")

        # Sending the voxelized mesh version to the front for rendering and visualisation
        with open("voxeled.obj", "r") as file:
            filedata = file.read()
            coded = base64.b64encode(bytes(filedata, encoding="utf-8"))
            file.close()
            os.remove("voxeled.obj")
            os.remove("voxeled.mtl")
        return jsonify({"data": str(coded, encoding="utf-8")}), 200
    else:
        errorLogger.error(request.path + " error ")
        return jsonify({"msg": "Data is empty"}), 400
