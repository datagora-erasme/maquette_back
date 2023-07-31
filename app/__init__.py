from flask import Flask, jsonify
from os import environ

# import pdfkit

from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint

# Import utils
from app.utils.constants import *
from app.utils.methods import *


# Import config.py file
from .config import config as app_config, ConfigDb


# Loading env vars from .env file
load_dotenv()
# Get current app_env
APPLICATION_ENV = get_environment()

# Create Flask app
app = Flask(app_config[APPLICATION_ENV].APP_NAME)
# Load variables from config file into app
app.config.from_object(app_config[APPLICATION_ENV])
app.config.from_object(ConfigDb)

# Loggers import
from loguru import logger as errorLogger, logger as infoLogger, logger as mailLogger
import logging
import os


db = SQLAlchemy(app)
ma = Marshmallow(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = app_config[APPLICATION_ENV].JWT_SECRET_KEY
jwt = JWTManager(app)


@jwt.expired_token_loader
def my_expired_token_callback(expired_token, jwt_payload):
    # Using the expired_token_loader decorator, we will now call
    # this function whenever an expired but otherwise valid access
    # token attempts to access an endpoint
    token_type = jwt_payload["type"]
    return (
        jsonify(
            {
                "status": 401,
                "sub_status": 42,
                "msg": "The {} token has expired".format(token_type),
            }
        ),
        401,
    )


# Set CORS policy (allow * origins)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# add Swagger-UI Blueprint
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
swaggerui_bp = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    "/api/docs",
    "/api/docs/swagger.json",
    config={  # Swagger UI config overrides
        "app_name": "Exo-Dev Swagger-UI",
        "persistAuthorization": True,
    },
    # oauth_config={
    #     # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #     'useBasicAuthenticationWithAccessCodeGrant': True
    # }
)

# Import Modules (only here)

from .core.views import core as core_bp
from .docs.views import docs as docs_bp
from .modules.authentications.views import authentications as authentications_bp
from .modules.users.views import users as users_bp

from .modules.projects.views import projects as projects_bp
from .modules.datas.views import datas as datas_bp

from .modules.dataprocess.views import dataprocess as dataprocess_bp

# Add BP to app routes
app.register_blueprint(swaggerui_bp, url_prefix="/api/docs")

app.register_blueprint(core_bp, url_prefix="/api/core")
app.register_blueprint(docs_bp, url_prefix="/api/docs")
app.register_blueprint(authentications_bp, url_prefix="/api/auth")
app.register_blueprint(users_bp, url_prefix="/api/users")


app.register_blueprint(projects_bp, url_prefix="/api/projects")
app.register_blueprint(datas_bp, url_prefix="/api/datas")
app.register_blueprint(dataprocess_bp, url_prefix="/api/dataprocess")
