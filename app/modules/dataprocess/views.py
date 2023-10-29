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
import random
import string

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

debug_mode = environ.get("DEBUG_MODE")


# Create Blueprint & get logger
dataprocess = Blueprint("dataprocess", __name__)
logger = LocalProxy(lambda: current_app.logger)


def voxelize(tempfile):
    """
    func: to use binvox for voxelization.
        @tempfile: the temp file created from the received Bbox.
    """
    if tempfile:
      if platform == "linux" or platform == "linux2":
          os.system("./binvox -e -ri -cb -fit -t msh " + tempfile)
      elif platform == "win32":
          os.system("binvox.exe -e -dc -v -ri -t msh " + tempfile)
    else:
        return jsonify({"msg": "File to voxelize isn't available"}), 400


@dataprocess.before_request
def before_request_func():
    current_app.logger.name = "dataprocess"


@dataprocess.route("/bbox", methods=["POST"])
def bboxreceive():
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
                    selected = gdfclip[gdfclip["strid"] == row["strid"]]
                    zt = {
                        "strid": row["strid"],
                        "geometry": j,
                        "hauteur": selected.hauteur[index],
                    }
                    info.append(zt)

        for i in info:
            if i["hauteur"]:
                m = trimesh.creation.extrude_polygon(i["geometry"], height=i["hauteur"])
                p.add_mesh(m, color="lightblue", opacity=1)
        saved_scene = ''.join(random.choices(string.ascii_lowercase, k=10))
        p.export_obj(saved_scene+".obj")
        # In case the Bbox contains no buildings
        if not p.mesh:
            return(jsonify({"msg": "Mesh is empty or contains no vectors", "isEmpty": "True"}), 400)
        # Voxelizing the tempfile that contains the mesh to voxelize
        voxelize(saved_scene+".obj")
        if debug_mode == 'False':
          os.remove(saved_scene+".obj")
          os.remove(saved_scene+".mtl")
        m = pv.Plotter()
        themesh = pv.read(saved_scene+".msh")

        m.add_mesh(themesh, color=True, show_edges=True, opacity=1)

        # Using Pyvista to export the voxelized version of the mesh
        p.export_obj(saved_scene+"_voxeled.obj")
        if debug_mode == 'False':
              os.remove(saved_scene+".msh")
      
        # Sending the voxelized mesh version to the front for rendering and visualisation
        with open(saved_scene+"_voxeled.obj", "r") as file:
            filedata = file.read()
            coded = base64.b64encode(bytes(filedata, encoding="utf-8"))
            file.close()
            if debug_mode == 'False':
              os.remove(saved_scene+"_voxeled.obj")
            os.remove(saved_scene+"_voxeled.mtl")
        return jsonify({"data": str(coded, encoding="utf-8")}), 200
    else:
        errorLogger.error(request.path + " error ")
        return jsonify({"msg": "Data is empty"}), 400
