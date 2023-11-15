from app.utils.constants import *
from app.utils.methods import *
from app import db, infoLogger, errorLogger
from app.models import Users, Authentications
from app.schemas import UserSchema, UserAdminSchema, UserListSchema
from os import environ
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.local import LocalProxy
from sqlalchemy import desc, asc, or_, func
from sqlalchemy.sql import text

# model import
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_admin_schema = UserAdminSchema()
users_admin_schema = UserAdminSchema(many=True)
user_select_schema = UserListSchema(many=True)

# Utils import


# Create Blueprint
users = Blueprint("users", __name__)


@users.before_request
def before_request_func():
    current_app.logger.name = "users"


@users.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all users
    ---
    tags:
      - users
    security:
      - Bearer: []
    responses:
      200:
        description: List all users
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # filters
    isName = False
    limit = None
    offset = None

    # ORDER BY
    order = asc("id")
    if "order_by" in request.args and "order_dir" in request.args:
        order = (
            asc(request.args["order_by"])
            if request.args["order_dir"] == "asc"
            else desc(request.args["order_by"])
        )

    # PAGINATE
    if (
        "nb_page" in request.args
        and "nb_items" in request.args
        and request.args["nb_page"]
        and request.args["nb_items"]
    ):
        try:
            form_nb_page = int(request.args["nb_page"])
            form_nb_items = int(request.args["nb_items"])

            limit = form_nb_items
            if form_nb_page:
                offset = (form_nb_page - 1) * form_nb_items
            else:
                offset = 0
        except:
            errorLogger.error("Fail to use nb_items & nb_page request.args")

    # FILTERS
    if "name" in request.args:
        isName = True

    count_users = Users.query.count()
    query = Users.query

    try:
        if isName:
            name_composed = request.args["name"].split(" ")
            if len(name_composed) > 1:
                query = query.filter(
                    or_(
                        func.concat(Users.firstname, " ", Users.lastname).ilike(
                            "%" + request.args["name"] + "%"
                        ),
                        func.concat(Users.lastname, " ", Users.firstname).ilike(
                            "%" + request.args["name"] + "%"
                        ),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Users.firstname.ilike("%" + request.args["name"] + "%"),
                        Users.lastname.ilike("%" + request.args["name"] + "%"),
                    )
                )
        if limit:
            if offset:
                users = query.order_by(order).limit(limit).offset(offset).all()
            else:
                users = query.order_by(order).limit(limit).all()
        else:
            users = query.order_by(order).all()

    except:
        errorLogger.error(
            "Error 500 : Internal Server Error - error filtering entities"
        )
        return jsonify({"msg": "Internal Server Error - error executing query"}), 500

    infoLogger.info("List " + str(len(users)) + " users")

    if currentUser["role"] == "SUPERADMIN":
        return (
            jsonify({"users": users_admin_schema.dump(users), "count": count_users}),
            200,
        )
    else:
        return jsonify({"users": users_schema.dump(users), "count": count_users}), 200


@users.route("select", methods=["GET"])
@jwt_required()
def listAllForSelect():
    """
    List all users for select list
    ---
    tags:
      - users
    security:
      - Bearer: []
    responses:
      200:
        description: List all users
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # ORDER BY
    order = text("lastname asc, firstname asc")
    query = Users.query

    try:
        if "name" in request.args and request.args["name"]:
            name_composed = request.args["name"].split(" ")
            print(request.args["name"])
            if len(name_composed) > 1:
                query = query.filter(
                    or_(
                        func.concat(Users.firstname, " ", Users.lastname).ilike(
                            "%" + request.args["name"] + "%"
                        ),
                        func.concat(Users.lastname, " ", Users.firstname).ilike(
                            "%" + request.args["name"] + "%"
                        ),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Users.firstname.ilike("%" + request.args["name"] + "%"),
                        Users.lastname.ilike("%" + request.args["name"] + "%"),
                    )
                )
    except:
        errorLogger.error(
            "Error 500 : Internal Server Error - error filtering entities"
        )
        return jsonify({"msg": "Internal Server Error - error executing query"}), 500

    users = query.order_by(order).all()

    infoLogger.info("List " + str(len(users)) + " users")
    return jsonify(user_select_schema.dump(users)), 200


@users.route("/<int:id>", methods=["GET"])
@jwt_required()
def getById(id):
    """
    Show user's information with his ID
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: User information
      404:
        description: Not found
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    user = Users.query.filter_by(id=id).first()

    if user is not None:
        if currentUser["role"] == "SUPERADMIN" or currentUser["id_user"] == user.id:
            return jsonify(user_admin_schema.dump(user)), 200
        else:
            return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify({"msg": "Not Found"}), 404


@users.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a user
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - firstname
            - lastname
            - authentication_id
          properties:
            authentication_id:
              type: integer
              description: ID of the Authentication's account
            firstname:
              type: string
              description: firstname of the user
            lastname:
              type: string
              description: lastname of the user
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

    # Get Body of request
    form = request.json

    if currentUser["role"] == "SUPERADMIN":
        if "firstname" in form and "lastname" in form and "authentication_id" in form:
            auth = Authentications.query.get(form["authentication_id"])

            if auth:

                newUser = Users(
                    authentication_id=auth.id,
                    firstname=form["firstname"],
                    lastname=form["lastname"],
                )

                db.session.add(newUser)
                db.session.commit()

                return jsonify({"msg": "OK", "id": newUser.id}), 200
            else:
                return jsonify({"msg": "Not Found"}), 404
        else:
            return jsonify({"msg": "Bad Request"}), 400
    else:
        return jsonify({"msg": "Forbidden"}), 403


@users.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def patchById(id):
    """
    Patch a user
    ---
    tags:
      - users
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
            firstname:
              type: string
              description: firstname of the user
            lastname:
              type: string
              description: lastname of the user
    responses:
      200:
        description: OK
      406:
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

    # Get Body of request
    form = request.json
    user = Users.query.get(id)

    # nullable inputs
    if user is not None:
        if currentUser["role"] == "SUPERADMIN" or currentUser["user_id"] == user.id:
      
            if "firstname" in form:
                user.firstname = form["firstname"]
            if "lastname" in form:
                user.lastname = form["lastname"]

            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found"}), 404


@users.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete a user
    ---
    tags:
      - users
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

    if "role" in currentUser and currentUser["role"] == "SUPERADMIN":
        user = Users.query.get(id)

        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Not Found"}), 404
    else:
        return jsonify({"msg": "Forbidden"}), 403
