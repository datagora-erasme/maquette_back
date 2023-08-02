from os import environ
from app import infoLogger, app
from flask import Blueprint, current_app, jsonify, request
from flask_swagger import swagger

# Utils import
from app.utils.constants import *
from app.utils.methods import *

# Create Blueprint & get logger
docs = Blueprint("docs", __name__)


@docs.before_request
def before_request_func():
    current_app.logger.name = "docs"


@docs.route("/swagger.json", methods=["GET"])
def getSwaggerUi():
    infoLogger.info(request.path)
    # Adding Package.json version to Swagger

    from pathlib import Path

    vers = Path("package.json").read_text().replace("\n", "").split('"')

    swag = swagger(app)
    swag["info"]["version"] = vers[7]
    swag["info"]["title"] = "Swagger Maquette Exo-dev API"

    env = environ.get("APPLICATION_ENV")
    if env == "production":
        swag["schemes"] = ["https", "http"]
    else:
        swag["schemes"] = ["https", "http"]

    swag["securityDefinitions"] = {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }

    return jsonify(swag), 200
