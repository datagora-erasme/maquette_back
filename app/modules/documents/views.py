from app import db, infoLogger, errorLogger
from app.models import Documents
from app.schemas import DocumentSchema, DocumentOnlySchema
from os import environ
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.local import LocalProxy

# model import
document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)
detail_document_schema = DocumentOnlySchema()

# Utils import
from app.utils.methods import *
from app.utils.constants import *


# Create Blueprint
documents = Blueprint("documents", __name__)

@documents.before_request
def before_request_func():
    current_app.logger.name = "documents"


@documents.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all documents
    ---
    tags:
      - documents
    security:
      - Bearer: []
    responses:
      200:
        description: List all documents
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    # currentUser = get_jwt_identity()

    documents = Documents.query.all()
    infoLogger.info("List " + str(len(documents)) + " documents")

    return jsonify(documents_schema.dump(documents)), 200


@documents.route("/<int:id>", methods=["GET"])
@jwt_required()
def getById(id):
    """
    Show documents' information with his ID
    ---
    tags:
      - documents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Documents information
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    # currentUser = get_jwt_identity()

    document = Documents.query.filter_by(id=id).first()

    if document is not None:
        return jsonify(detail_document_schema.dump(document)), 200
    else:
        return jsonify({"msg": "Not Found"}), 404


@documents.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a document
    ---
    tags:
      - documents
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - title
            - type
            - file_name
            - data
          properties:
            title:
              type: string
              description: title of the document
            type:
              type: string
              description: type of document []
            file_name:
              type: string
              description: name of the file for DL
            data:
              type: string
              description: base64 of the document
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

    if "role" in currentUser and currentUser["role"] == "USER":
        return jsonify({"msg": "Forbidden"}), 403

    # Get Body of request
    form = request.json

    if "title" in form and "type" in form and "data" in form and "file_name" in form:
        newDocument = Documents(
            # required
            date_create=datetime.datetime.utcnow(),
            user_id=currentUser["user_id"],
            title=form["title"],
            type=form["type"],
            file_name=form["file_name"],
            data=form["data"],
        )

        db.session.add(newDocument)
        db.session.commit()

        return jsonify({"msg": "OK", "id": newDocument.id}), 200
    else:
        return jsonify({"msg": "Bad Request"}), 400


@documents.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def updateById(id):
    """
    Update a document
    ---
    tags:
      - documents
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
            title:
              type: string
              description: title of the document
            type:
              type: string
              description: type of document []
            file_name:
              type: string
              description: name of the file for DL
            data:
              type: string
              description: base64 of the document
    responses:
      200:
        description: Skill updated with success
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
    document = Documents.query.get(id)

    if document is not None:
        has_access = False
        if "role" in currentUser and currentUser["role"] == "SUPERADMIN":
            has_access = True
        elif document.user_id == currentUser["user_id"]:
            has_access = True

        if has_access:
            if "title" in form:
                document.title = form["title"]
            if "file_name" in form:
                document.file_name = form["file_name"]
            if "type" in form:
                document.type = form["type"]
            if "data" in form:
                document.data = form["data"]

            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found"}), 404


@documents.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete a document
    ---
    tags:
      - documents
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
        description: Bad Request
      404:
        description: Not Found
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    document = Documents.query.get(id)

    if document:
        has_access = False
        if "role" in currentUser and currentUser["role"] == "SUPERADMIN":
            has_access = True
        elif document.user_id == currentUser["user_id"]:
            has_access = True

        if has_access:
            db.session.delete(document)
            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Forbidden"}), 401
    else:
        return jsonify({"msg": "Not Found"}), 404
