import os
import sys
import psycopg2
from os import environ, path
from dotenv import load_dotenv
from loguru import logger as errorLogger
from app.utils.methods import hashStringWithSaltB64
import argparse

# Get app base directory
basedir = path.abspath(path.join(path.dirname(__file__), ".."))
# loading env vars from .env file
load_dotenv()


parser = argparse.ArgumentParser("run.py")
parser.add_argument('-e', '--email', help="The email you want to use for the demo account", type=str)
parser.add_argument('-p', '--password', help="The password you want to use for the demo account", type=str)
args = parser.parse_args()

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

def dbchecker(conn, check):
            exists = False
            try:
                cur = conn.cursor()
                cur.execute(check)
                exists = cur.fetchone()[0]
                cur.close()
            except psycopg2.Error as e:
                errorLogger.error(e)
            return exists

def sql_execute(conn, commands, f):
            try:
                cur = conn.cursor()
                if f:
                    cur.execute(open(commands, "r").read())
                else:
                    cur.execute(commands)
                cur.close()
            except psycopg2.Error as e:
                errorLogger.error(e)

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
            conn.autocommit = True
            if not dbchecker(conn,"select exists(select relname from pg_class where relname='authentications')"):
                sql_execute(conn,"sql/create-tables.sql", True)
                cmd = "INSERT INTO base.authentications (email, password, role, status) VALUES ('%s', '%s', 'SUPERADMIN', 'ACTIVE');" % (args.email, hashStringWithSaltB64(args.password))
                sql_execute(conn,cmd, False)
                uid = dbchecker(conn,"SELECT id FROM base.authentications WHERE email = '" + args.email + "'")
                sql_execute(conn,"INSERT INTO base.users (firstname, lastname, authentication_id) VALUES ('Démo', 'Métropole', '" + str(uid) + "');", False)
                conn.close()
            else:
                if not dbchecker(conn,"select exists(select email from base.authentications where email='" + args.email + "')"):
                    cmd = "INSERT INTO base.authentications (email, password, role, status) VALUES ('%s', '%s', 'SUPERADMIN', 'ACTIVE');" % (args.email, hashStringWithSaltB64(args.password))
                    sql_execute(conn,cmd, False)
                    uid = dbchecker(conn,"SELECT id FROM base.authentications WHERE email = '" + args.email + "'")
                    sql_execute(conn,"INSERT INTO base.users (firstname, lastname, authentication_id) VALUES ('Démo', 'Métropole', '" + str(uid) + "');", False)
                    conn.close()
        except psycopg2.Error as e:
            errorLogger.error(e)
            sys.exit(1)
    else:
        print(f'config_user="{config_user}"')
        print(f'config_pwd="{config_pwd}"')
        print(f'config_host="{config_host}"')
        print(f'config_db="{config_db}"')
        print(f'config_port="{config_port}"')
        print("ERROR: Something is wrong about DB credentials")
        sys.exit(1)
