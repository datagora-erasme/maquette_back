from ast import Sub
from app import db, infoLogger, errorLogger
from app.models import Contacts, Customers
from app.schemas import ContactSchema
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc, or_, func
from sqlalchemy.sql import text
from werkzeug.local import LocalProxy
import xlsxwriter

# model import
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

# Utils import
from app.utils.methods import *
from app.utils.constants import *


# Create Blueprint & get logger
contacts = Blueprint("contacts", __name__)
logger = LocalProxy(lambda: current_app.logger)


@contacts.before_request
def before_request_func():
    current_app.logger.name = "contacts"


@contacts.route("", methods=["GET"])
# @contacts.route("/select", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all contacts
    ---
    tags:
      - contacts
    security:
      - Bearer: []
    parameters:
      - in: query
        name: order_by
        schema:
          type: string
        description: field for applying the ORDER
      - in: query
        name: order_dir
        schema:
          type: string
        description: direction of the ORDER (asc OR desc)
      - in: query
        name: nb_page
        schema:
          type: integer
        description: Number of the "page" to fetch
      - in: query
        name: nb_items
        schema:
          type: integer
        description: Number of items to fetch
      - in: query
        name: customer_id
        schema:
          type: integer
        description: ID of the Customer to filter
      - in: query
        name: name
        schema:
          type: string
        description: name of the Contact
    responses:
      200:
        description: List all contacts
      500:
        description: Internal Server Error
    """
    infoLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    limit = None
    offset = None

    # ORDER BY
    order = text("lastname asc, firstname asc")
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
            infoLogger.info("Fail to use nb_items & nb_page request.args")

    query = Contacts.query

    # FILTER
    try:
        if "customer_id" in request.args and request.args["customer_id"]:
            query = query.join(Contacts.customer).filter_by(
                id=request.args["customer_id"]
            )
        if "name" in request.args and request.args["name"]:
            name_composed = request.args["name"].lower().split(" ")
            if len(name_composed) > 1:
                query = query.filter(
                    or_(
                        func.concat(Contacts.firstname, " ", Contacts.lastname).ilike(
                            "%" + escapeForDBFilter(request.args["name"]) + "%"
                        ),
                        func.concat(Contacts.lastname, " ", Contacts.firstname).ilike(
                            "%" + escapeForDBFilter(request.args["name"]) + "%"
                        ),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Contacts.firstname.ilike(
                            "%" + escapeForDBFilter(request.args["name"]) + "%"
                        ),
                        Contacts.lastname.ilike(
                            "%" + escapeForDBFilter(request.args["name"]) + "%"
                        ),
                    )
                )
    except:
        if not isDevEnv():
            errorLogger.error(
                "Error 500 : Internal Server Error - error filtering entities"
            )
            return (
                jsonify({"msg": "Internal Server Error - error filtering entities"}),
                500,
            )

    count_entities = query.count()
    if limit:
        if offset:
            datas = query.order_by(order).limit(limit).offset(offset).all()
        else:
            datas = query.order_by(order).limit(limit).all()
    else:
        datas = query.order_by(order).all()

    infoLogger.info("List " + str(len(datas)) + " contacts")

    return (
        jsonify({"contacts": contacts_schema.dump(datas), "count": count_entities}),
        200,
    )


@contacts.route("/<int:id>", methods=["GET"])
@jwt_required()
def getById(id):
    """
    Show contact's information with his ID
    ---
    tags:
      - contacts
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Contact information
      403:
        description: Forbidden
      404:
        description: Not found
    """
    infoLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    contact = Contacts.query.get(id)

    if contact is not None:
        if currentUser["role"] in ("SUPERADMIN", "ADMIN"):
            return jsonify(contact_schema.dump(contact)), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found"}), 404


@contacts.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def patchById(id):
    """
    Patch a contact
    ---
    tags:
      - contacts
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
          required:
          properties:
            firstname:
              type: string
              description: firstname of the contact
            lastname:
              type: string
              description: lastname of the contact
            email:
              type: string
              description: mail of the contact
            phone:
              type: string
              description: phone number of the contact
            job_title:
              type: string
              description: job title of the contact
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
    infoLogger.info(request.path + " PATCH")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Get Body of request
    form = request.json
    contact = Contacts.query.get(id)

    # nullable inputs
    if "phone" not in form or ("phone" in form and form["phone"] == None):
        form["phone"] = None
    elif "phone" in form and len(form["phone"]) == 0:
        form["phone"] = None

    if contact is not None:
        if currentUser["role"] in ("SUPERADMIN", "ADMIN"):
            if "firstname" in form and form["firstname"]:
                contact.firstname = form["firstname"]
            if "lastname" in form and form["lastname"]:
                contact.lastname = form["lastname"]
            if "email" in form and form["email"]:
                contact.email = form["email"]
            if "job_title" in form and form["job_title"]:
                contact.job_title = form["job_title"]

            if form["phone"] != None:
                contact.phone = form["phone"]

            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found : Contact"}), 404


@contacts.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete a contact
    ---
    tags:
      - contacts
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
    infoLogger.info(request.path + " DELETE")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    if "role" in currentUser and currentUser["role"] in ("SUPERADMIN"):
        contact = Contacts.query.get(id)

        if contact:
            db.session.delete(contact)
            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Not Found"}), 404
    else:
        return jsonify({"msg": "Forbidden"}), 403


@contacts.route("/export", methods=["GET"])
@jwt_required()
def exportContacts():
    """
    Export contacts
    ---
    tags:
      - contacts
    security:
      - Bearer: []
    parameters:
      - in: query
        name: order_by
        schema:
          type: string
        description: field for applying the ORDER
      - in: query
        name: order_dir
        schema:
          type: string
        description: direction of the ORDER (asc OR desc)
      - in: query
        name: customer_id
        schema:
          type: integer
        description: ID of the Customer to filter
      - in: query
        name: name
        schema:
          type: string
        description: name of the Contact
    responses:
      200:
        description: Export contacts
      500:
        description: Internal Server Error
    """
    infoLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # ORDER BY
    order = text("lastname asc, firstname asc")
    if "order_by" in request.args and "order_dir" in request.args:
        order = (
            asc(request.args["order_by"])
            if request.args["order_dir"] == "asc"
            else desc(request.args["order_by"])
        )

    query = Contacts.query

    if currentUser["role"] in ("SUPERADMIN", "ADMIN"):
        # FILTER
        try:
            if "customer_id" in request.args and request.args["customer_id"]:
                query = query.join(Contacts.customer).filter_by(
                    id=request.args["customer_id"]
                )
            if "name" in request.args and request.args["name"]:
                name_composed = request.args["name"].lower().split(" ")
                if len(name_composed) > 1:
                    query = query.filter(
                        or_(
                            func.concat(
                                Contacts.firstname, " ", Contacts.lastname
                            ).ilike(
                                "%" + escapeForDBFilter(request.args["name"]) + "%"
                            ),
                            func.concat(
                                Contacts.lastname, " ", Contacts.firstname
                            ).ilike(
                                "%" + escapeForDBFilter(request.args["name"]) + "%"
                            ),
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            Contacts.firstname.ilike(
                                "%" + escapeForDBFilter(request.args["name"]) + "%"
                            ),
                            Contacts.lastname.ilike(
                                "%" + escapeForDBFilter(request.args["name"]) + "%"
                            ),
                        )
                    )
            count_entities = query.count()
            contacts = query.order_by(order).all()

            name_filter = ""
            if "customer_id" in request.args and request.args["customer_id"]:
                name_filter += "customer-" + request.args["customer_id"] + "_"

            name_export = (
                "contacts_"
                + name_filter
                + datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
                + ".xlsx"
            )
            path_file = environ.get("PATH_GENERATED_FILES") + "csv/" + name_export

            workbook = xlsxwriter.Workbook(path_file)
            worksheet = workbook.add_worksheet("Liste des Contacts")

            cellsFormats = getXlsxCellsFormat(workbook)

            columns = [
                "ID",
                "Date de création",
                "Nom",
                "Prénom",
                "Mail",
                "Téléphone",
                "Poste",
                "Entité liée",
            ]
            row = 1
            col = 0

            for item in columns:
                worksheet.write(0, col, item, cellsFormats["header_cell_format"])
                col += 1

            for contact in contacts:
                # computed fields
                if contact.customer:
                    linked_entity = "Client - " + contact.customer.name
                else:
                    linked_entity = ""

                col = 0
                worksheet.write(
                    row, col, contact.id, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.date_create, cellsFormats["date_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.lastname, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.firstname, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.email, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.phone, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, contact.job_title, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, linked_entity, cellsFormats["default_cell_format"]
                )
                col += 1

                row += 1

            worksheet.write(row + 1, 0, "Nombre :", cellsFormats["header_cell_format"])
            worksheet.write(
                row + 1, 1, len(contacts), cellsFormats["default_cell_format"]
            )

            worksheet.autofit()

            workbook.close()
            data = exportFileToBase64(path_file)

            # delete physical file and download it
            os.remove(path_file)

            return (
                jsonify(
                    {
                        "filename": name_export,
                        "nb_datas": len(contacts),
                        "data": str(data),
                    }
                ),
                200,
            )
        except Exception as error:
            # delete file if created
            try:
                os.remove(path_file)
            except:
                infoLogger.info("No need to delete export file")
            error_str = " ".join(str(error).split())
            errorLogger.error(error_str)
            if isDevEnv():
                return (
                    jsonify({"msg": "Internal Server Error", "error": error_str}),
                    500,
                )
            else:
                return jsonify({"msg": "Internal Server Error"}), 500
    else:
        return jsonify({"msg": "Forbidden"}), 403
