import os
import sys
import psycopg2
from os import environ, path
from dotenv import load_dotenv
from loguru import logger as errorLogger

# Get app base directory
basedir = path.abspath(path.join(path.dirname(__file__), ".."))
# loading env vars from .env file
load_dotenv()


class BaseConfig(object):
    """Base config class."""

    APP_NAME = environ.get("APP_NAME")
    HOST = environ.get("APP_HOST")
    PORT = environ.get("APP_PORT")
    ORIGINS = ["*"]
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SOCKETIO_SECRET_KEY = os.getenv("SOCKETIO_SECRET_KEY")
    PDF_KIT = os.getenv("WK_HTMLTOPDF")

    EMAIL_CHARSET = "UTF-8"

    LOG_INFO_FILE = path.join(basedir, "log", "info.log")
    LOG_ERROR_FILE = path.join(basedir, "log", "error.log")

    BDD_CONFIG = {
        "host": os.getenv("BDD_CONFIG_HOST"),
        "user": os.getenv("BDD_CONFIG_USER"),
        "passwd": os.getenv("BDD_CONFIG_PASSWD"),
        "db": os.getenv("BDD_CONFIG_DB"),
    }


class Development(BaseConfig):
    """Development config."""

    DEBUG = True
    ENV = "dev"
    APP_NAME = environ.get("DEV_APP_NAME")


class Staging(BaseConfig):
    """Staging config."""

    DEBUG = True
    ENV = "staging"
    APP_NAME = environ.get("STAGING_APP_NAME")


class Production(BaseConfig):
    """Production config"""

    DEBUG = False
    ENV = "production"
    APP_NAME = environ.get("PROD_APP_NAME")


config = {
    "development": Development,
    "staging": Staging,
    "production": Production,
}


class ConfigDb(BaseConfig):
    config_user = environ.get("BDD_CONFIG_USER")
    config_pwd = environ.get("BDD_CONFIG_PASSWD")
    config_host = environ.get("BDD_CONFIG_HOST")
    config_db = environ.get("BDD_CONFIG_DB")
    config_port = environ.get("BDD_CONFIG_PORT")

    if config_user and config_pwd and config_host and config_db and config_port:
        # conf SQLALCHEMY for manage pool queue
        POOL_PRE_PING = True
        POOL_SIZE = 32
        MAX_OVERFLOW = 64
        # DB conf for SQLALCHEMY
        SQLALCHEMY_DATABASE_URI = (
            "postgresql+psycopg2://"
            + config_user
            + ":"
            + config_pwd
            + "@"
            + config_host
            + ":"
            + config_port
            + "/"
            + config_db
        )
        SQLALCHEMY_TRACK_MODIFICATIONS = False

        try:
            conn = psycopg2.connect(
                f"dbname='{config_db}' user='{config_user}' host='{config_host}' password='{config_pwd}' port='{config_port}'"
            )
            conn.close()
        except:
            errorLogger.error(
                "ERROR: Fail to connect to DB with "
                + " "
                + config_db
                + " "
                + config_user
                + " "
                + config_host
                + " "
                + config_pwd
                + " "
                + config_port
            )
            sys.exit(1)
    elif config_user and config_port and config_host and config_db:
        # conf SQLALCHEMY for manage pool queue
        POOL_PRE_PING = True
        POOL_SIZE = 32
        MAX_OVERFLOW = 64
        # DB conf for SQLALCHEMY
        SQLALCHEMY_DATABASE_URI = (
            "postgresql+psycopg2://"
            + config_user
            + ":"
            + config_pwd
            + "@"
            + config_host
            + ":"
            + config_port
            + "/"
            + config_db
        )
        SQLALCHEMY_TRACK_MODIFICATIONS = False

        try:
            conn = psycopg2.connect(
                f"dbname='{config_db}' user='{config_user}' host='{config_host}' password='{config_pwd}' port='{config_port}'"
            )
            conn.close()
        except:
            errorLogger.error(
                "ERROR: Fail to connect to DB with "
                + " "
                + config_db
                + " "
                + config_user
                + " "
                + config_host
                + " "
                + config_pwd
                + " "
                + config_port
            )
            sys.exit(1)
    else:
        print(f'config_user="{config_user}"')
        print(f'config_pwd="{config_pwd}"')
        print(f'config_host="{config_host}"')
        print(f'config_db="{config_db}"')
        print(f'config_port="{config_port}"')
        print("ERROR: Something is wrong about DB credentials")
        sys.exit(1)
