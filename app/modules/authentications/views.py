from app.files.content_mails import *
from app.utils.mails import *
from app.utils.methods import *
from app.utils.constants import *
from app.models import Authentications, Users
from app.schemas import AuthenticationSchema
from app import db, infoLogger, errorLogger
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.local import LocalProxy
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# model import
auth_schema = AuthenticationSchema()
auths_schema = AuthenticationSchema(many=True)

# Utils import

# Content mails import

# Create Blueprint
authentications = Blueprint("authentications", __name__)


@authentications.before_request
def before_request_func():
    current_app.logger.name = "authentications"


@authentications.route("/login", methods=["POST"])
def loginAuth():
    """
    Login to the app
    ---
    tags:
      - authentications
    parameters:
      - in: body
        name: body
        schema:
          required:
            - login
            - password
          properties:
            login:
              type: string
              description: login of the user
            password:
              type: string
              description: password of the user
    responses:
      200:
        description: Token created
      400:
        description: Login or password incorrect
      403:
        description: Forbidden
    """
    infoLogger.info(f"{request.method} → {request.path}")

    records = []
    ip_address = request.remote_addr
    expires = timedelta(hours=24)

    if request.json and "login" in request.json and "password" in request.json:
        # Get Body of request
        loginForm = request.json["login"]
        passwordForm = request.json["password"]

        sqlListAuthentications = Authentications.query.filter(
            Authentications.email == loginForm
        )

        for authentication in sqlListAuthentications:
            records.append(authentication)

        if records and len(records) == 1:
            authDB = records[0]

            # Get stored key and decode all
            storKeyDecode = decodeB64(authDB.password)
            # Get stored salt
            storSalt = storKeyDecode[:32]
            # Encrypt passed password SHA256 to compare
            userPasswordHash = hashStringWithSaltB64(passwordForm, storSalt)

            if authDB.status == "PENDING":
                return (
                    jsonify(
                        {"msg": "Forbidden : Account pending", "status": "pending"}
                    ),
                    403,
                )
            elif authDB.status == "BANNED":
                return (
                    jsonify({"msg": "Forbidden : Account banned", "status": "banned"}),
                    403,
                )
            elif not authDB.password == userPasswordHash:
                return (
                    jsonify({"msg": "Login or password incorrect", "status": "error"}),
                    400,
                )
            else:
                user = Users.query.filter(Users.authentication_id == authDB.id).first()

                # create token
                userIdentity = {
                    "id": authDB.id,
                    "role": authDB.role,
                    "status": authDB.status,
                    "ip": ip_address,
                    "email": authDB.email,
                    "user_id": user.id,
                }
                # Create Token
                access_token = create_access_token(
                    identity=userIdentity, expires_delta=expires
                )

                response = jsonify({"token": access_token, "firstname": user.firstname, "lastname": user.lastname})
                response.status_code = 200
                # add token to response headers - so SwaggerUI can use it
                response.headers.extend({"jwt-token": access_token})

                return response
        else:
            return (
                jsonify({"msg": "Login or password is incorrect", "status": "error"}),
                400,
            )
    else:
        return jsonify({"msg": "Bad Request", "status": "error"}), 400


@authentications.route("/logout", methods=["GET"])
@jwt_required()
def logoutAuth():
    infoLogger.info(f"{request.method} → {request.path}")

    # delete token ?
    return jsonify({"msg": "You're now logout"}), 200


@authentications.route("/user", methods=["GET"])
@jwt_required()
def getUserDatas():
    """
    Get user informations with the Token
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    responses:
      200:
        description: User's informations
      404:
        description: Not Found
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    userDB = Users.query.filter(Users.authentication_id == currentUser["id"]).first()

    if userDB:
        authUser = {
            "id": currentUser["id"],
            "role": currentUser["role"],
            "status": currentUser["status"],
            "email": currentUser["email"],
            "id_user": userDB.id,
            "firstname": userDB.firstname,
            "lastname": userDB.lastname,
        }

        return jsonify({"user": authUser}), 200
    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("/token", methods=["GET"])
@jwt_required()
def checkToken():
    """
    Check the validity of the Token
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    responses:
      200:
        description: OK
      400:
        description: Bad Request
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Request IP
    actualIp = request.remote_addr
    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    # Load JSON
    tokenIp = currentUser["ip"]

    if actualIp == tokenIp:
        return jsonify({"msg": "OK"}), 200
    else:
        return jsonify({"msg": "Bad Request : IP Adress is incorrect"}), 400


@authentications.route("/temp_token", methods=["GET"])
@jwt_required()
def checkTempToken():
    """
    Check the validity of the Temporary Token
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    responses:
      200:
        description: OK
      400:
        description: Bad Request
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Load JSON
    authentication = Authentications.query.get(currentUser["id"])

    if authentication:
        if authentication.email == currentUser["email"]:
            return jsonify({"msg": "OK", "status": authentication.status}), 200
        else:
            return jsonify({"msg": "Bad Request : Invalid Token"}), 400
    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("/check/<string:email>", methods=["GET"])
@jwt_required()
def checkEmail(email):
    """
    Check if the email exists already 
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: email
        type: string
        required: true
    responses:
      200:
        description: There is already a user with this email / No users with this email
    """
    infoLogger.info(f"{request.method} → {request.path}")

    authentications = Authentications.query.filter_by(email=email).all()

    if authentications:
        return (
            jsonify(
                {"msg": "There is already a user with this email", "isExisting": True}
            ),
            200,
        )
    else:
        return jsonify({"msg": "No users with this email", "isExisting": False}), 200


@authentications.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all Authentications accounts
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    responses:
      200:
        description: List of all accounts
      403:
        description: Forbidden
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    if currentUser["role"] == "SUPERADMIN":
        authentications = Authentications.query.all()
        infoLogger.info("List " + str(len(authentications)) + " authentications")
        return jsonify(auths_schema.dump(authentications)), 200
    else:
        return jsonify({"msg": "Forbidden"}), 403


@authentications.route("/<int:id>", methods=["GET"])
@jwt_required()
def getById(id):
    """
    Get an Authentication account by ID
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Authentication's account
      403:
        description: Forbidden
      404:
        description: Not Found
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    authentication = Authentications.query.get(id)

    if authentication:
        if currentUser["role"] == "SUPERADMIN":
            return jsonify(auth_schema.dump(authentication)), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a new authentication's account
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - email
            - role
          properties:
            email:
              type: string
              description: email of the user account
            role:
              type: string
              description: role of the user account ['SUPERADMIN', 'USER', 'ADMIN']
    responses:
      200:
        description: OK
      400:
        description: Bad Request
      403:
        description: Forbidden
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    expire_time = 48
    expires = timedelta(hours=expire_time)

    if currentUser["role"] == "SUPERADMIN":
        # Get Body of request
        form = request.json

        if "email" in form:
            verif_mail = Authentications.query.filter_by(email=form["email"]).all()

            if len(verif_mail) > 0:
                return jsonify({"msg": "Bad Request : account already exist"}), 400

        if "email" in form and "role" in form:
            pwd = pwdGenerator(12)

            newAuth = Authentications(
                email=form["email"],
                password=hashStringWithSaltB64(pwd),
                status="PENDING",
                role=form["role"],
            )

            db.session.add(newAuth)
            db.session.commit()

            # generate email
            server = ServerSMTP()
            sender = str(os.getenv("SMTP_SENDER"))
            to = [str(newAuth.email)]
            subject = "Bienvenue dans le projet Maquette!"
            codage = "UTF-8"
            typetext = "html"

            # create temporary token (48heures)
            userIdentity = {"id": newAuth.id, "email": newAuth.email}

            temporary_token = create_access_token(
                identity=userIdentity, expires_delta=expires
            )
            url_link = os.getenv("APPLICATION_URL") + "valid?token=" + temporary_token

            corpsWithDatas = corps_new_user.format(
                url_link, str(expire_time) + "h", os.getenv("CONTACT_MAIL_HELP")
            )
            corps = (
                header_mail_template.format(subject)
                + corpsWithDatas
                + footer_mail_template
            )

            try:
                msg = MessageSMTP(
                    sender=sender,
                    to=to,
                    subject=subject,
                    corps=corps,
                    codage=codage,
                    typetext=typetext,
                )

                rep = sendSMTP(msg, server)

                if rep == "":
                    infoLogger.info("mail sent : " + str(to))
                    return jsonify({"msg": "OK", "id": newAuth.id}), 200
                else:
                    errorLogger.error(str(rep))
                    return (
                        jsonify({"msg": "Internal Server Error : sending the email"}),
                        500,
                    )
            except:
                errorLogger.error(
                    request.path
                    + " Error creating MessageSMTP object : %s" % sys.exc_info()[1]
                )
                return (
                    jsonify({"msg": "Internal Server Error : creating the email"}),
                    500,
                )

        else:
            return jsonify({"msg": "Bad Request"}), 400
    else:
        return jsonify({"msg": "Forbidden"}), 403


@authentications.route("/reset", methods=["POST"])
def resetPassword():
    """
    Ask a reset password's process
    ---
    tags:
      - authentications
    parameters:
      - in: body
        name: body
        schema:
          required:
            - email
          properties:
            email:
              type: string
              description: email of the user account
    responses:
      200:
        description: OK
      400:
        description: Bad Request
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Get Body of request
    form = request.json
    ip_address = request.remote_addr
    expire_time = 30
    expires = timedelta(minutes=expire_time)

    if "email" in form:
        authDB = Authentications.query.filter_by(email=form["email"]).first()

        if authDB:
            userIdentity = {"id": authDB.id, "ip": ip_address, "email": authDB.email}

            # Create Token
            temporary_token = create_access_token(
                identity=userIdentity, expires_delta=expires
            )
            url_link = os.getenv("APPLICATION_URL") + "reset?token=" + temporary_token

            # generate email
            server = ServerSMTP()
            sender = str(os.getenv("SMTP_SENDER"))
            to = [str(authDB.email)]
            subject = "Processus de réinitialisation de mot de passe"
            codage = "UTF-8"
            typetext = "html"

            corpsWithDatas = corps_reset_password.format(
                url_link, str(expire_time) + " minutes"
            )
            corps = (
                header_mail_template.format(subject)
                + corpsWithDatas
                + footer_mail_template
            )

            try:
                msg = MessageSMTP(
                    sender=sender,
                    to=to,
                    subject=subject,
                    corps=corps,
                    codage=codage,
                    typetext=typetext,
                )

                rep = sendSMTP(msg, server)

                if rep == "":
                    infoLogger.info("mail sent : " + str(to))
                    return jsonify({"msg": "OK"}), 200
                else:
                    errorLogger.error(rep)
                    return (
                        jsonify({"msg": "Internal Server Error : sending the email"}),
                        500,
                    )
            except:
                errorLogger.error(
                    request.path
                    + " Error creating MessageSMTP object : %s" % sys.exc_info()[1]
                )
                return (
                    jsonify({"msg": "Internal Server Error : creating the email"}),
                    500,
                )
    else:
        return jsonify({"msg": "Bad Request"}), 400


@authentications.route("", methods=["PATCH"])
@jwt_required()
def patchByJWT():
    """
    Patch is own authentication (by JWT)
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          properties:
            email:
              type: string
              description: email of the user account
            password:
              type: string
              description: password of the user account
    responses:
      200:
        description: Authentication's account updated with success
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

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    id = currentUser["id"]

    # Get Body of request
    form = request.json

    authentication = Authentications.query.get(id)

    if authentication:
        # case activate account
        if authentication.status == "PENDING":
            authentication.status = "ACTIVE"
            if form and "password" in form:
                authentication.password = hashStringWithSaltB64(form["password"])
                db.session.commit()
                return jsonify({"msg": "OK", "is_activated": True}), 200
            else:
                return jsonify({"msg": "Bad Request", "is_activated": False}), 400

        elif authentication.status == "ACTIVE":
            if "email" in request.json:
                authentication.email = form["email"]
            if "password" in request.json:
                authentication.password = hashStringWithSaltB64(form["password"])

            db.session.commit()
            return jsonify({"msg": "OK", "is_activated": False}), 200
        else:
            return jsonify({"msg": "Forbidden : Account is banned or inactive"}), 403
    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def patchById(id):
    """
    Patch an authentication's account by ID
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: false
      - in: body
        name: body
        schema:
          properties:
            email:
              type: string
              description: email of the user account
            role:
              type: string
              description: role of the user account ['SUPERADMIN', 'USER', 'ADMIN']
            status:
              type: string
              description: status of the user account ['INACTIVE', 'ACTIVE', 'BANNED', 'PENDING']
    responses:
      200:
        description: OK
      403:
        description: Forbidden
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Get Body of request
    form = request.json

    authentication = Authentications.query.get(id)

    if authentication:
        if "role" in currentUser and currentUser["role"] == "SUPERADMIN":
            if "email" in form:
                authentication.email = form["email"]
            if "status" in form:
                authentication.status = form["status"]
            if "role" in form:
                authentication.role = form["role"]
        else:
            return jsonify({"msg": "Forbidden"}), 403

        db.session.commit()
        return jsonify({"msg": "OK"}), 200
    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("/<int:id>/send_mail", methods=["GET"])
@jwt_required()
def resendMailsValidAccount(id):
    """
    Resend email to the user for first step or validate his account
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: OK
      403:
        description: Forbidden
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    authentication = Authentications.query.get(id)

    if authentication:
        if authentication.status == "ACTIVE":
            return (
                jsonify(
                    {"msg": "This account is already active", "id": authentication.id}
                ),
                200,
            )
        elif authentication.status == "BANNED":
            return (
                jsonify({"msg": "This account is banned", "id": authentication.id}),
                403,
            )
        else:
            if authentication.status == "INACTIVE":
                authentication.status = "PENDING"

            expire_time = 24
            expires = timedelta(hours=expire_time)

            # generate email
            server = ServerSMTP()
            sender = str(os.getenv("SMTP_SENDER"))
            to = [str(authentication.email)]
            subject = "Invitation à activer son compte"
            codage = "UTF-8"
            typetext = "html"

            # create temporary token (24h)
            userIdentity = {"id": authentication.id, "email": authentication.email}
            temporary_token = create_access_token(
                identity=userIdentity, expires_delta=expires
            )
            url_link = os.getenv("APPLICATION_URL") + "valid?token=" + temporary_token

            corpsWithDatas = corps_new_user.format(
                url_link, os.getenv("CONTACT_MAIL_HELP"), str(expire_time) + "h"
            )
            corps = (
                header_mail_template.format(subject)
                + corpsWithDatas
                + footer_mail_template
            )

            try:
                msg = MessageSMTP(
                    sender=sender,
                    to=to,
                    subject=subject,
                    corps=corps,
                    codage=codage,
                    typetext=typetext,
                )
                rep = sendSMTP(msg, server)
                if rep == "":
                    infoLogger.info("mail sent : " + str(to))
                    return jsonify({"msg": "OK"}), 200
                else:
                    errorLogger.error(rep)
                    return (
                        jsonify(
                            {"msg": "Internal Server Error : fail to send the email"}
                        ),
                        500,
                    )
            except:
                errorLogger.error(
                    request.path
                    + " Error creating MessageSMTP object : %s" % sys.exc_info()[1]
                )
                return (
                    jsonify(
                        {"msg": "Internal Server Error : creating MessageSMTP object"}
                    ),
                    500,
                )

    else:
        return jsonify({"msg": "Not Found"}), 404


@authentications.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete an authentication's account
    ---
    tags:
      - authentications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: OK
      403:
        description: Forbidden
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    if currentUser["role"] == "SUPERADMIN":
        auth = Authentications.query.get(id)

        if auth:
            db.session.delete(auth)
            db.session.commit()

            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Not Found"}), 404
    else:
        return jsonify({"msg": "Forbidden"}), 403
