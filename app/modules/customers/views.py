from app import db, infoLogger, errorLogger
from app.models import Customers, Users, Authentications
from app.models import Documents, Contacts, Notifications, NotificationsUsers
from app.schemas import CustomerListSchema, CustomerSchema
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.local import LocalProxy
from sqlalchemy import desc, asc
from str2bool import str2bool
import xlsxwriter

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customers_list_schema = CustomerListSchema(many=True)

# Utils import
from app.utils.methods import *
from app.utils.constants import *


# Create Blueprint & get logger
customers = Blueprint("customers", __name__)
logger = LocalProxy(lambda: current_app.logger)


@customers.before_request
def before_request_func():
    current_app.logger.name = "customers"


@customers.route("", methods=["GET"])
@customers.route("/select", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all customers (list/select list)
    ---
    tags:
      - customers
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
        name: name
        schema:
          type: string
        description: name of the customer
      - in: query
        name: status
        schema:
          type: string
        description: status of the customer [PREPARATION, STEP_1, STEP_2, END_MISSION, INACTIVE, ARCHIVED]
      - in: query
        name: is_individual
        schema:
          type: boolean
        description: if the customer is an individual or a company
    responses:
      200:
        description: List all customers
      403:
        description: Forbidden
      500:
        description: Internal Server Error
    """
    errorLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    limit = None
    offset = None

    # ORDER BY
    order = asc("name")
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
            errorLogger.info("Fail to use nb_items & nb_page request.args")

    query = Customers.query

    try:
        if "name" in request.args and request.args["name"]:
            query = query.filter(
                Customers.name.ilike(
                    "%" + escapeForDBFilter(request.args["name"]) + "%"
                )
            )
        if "status" in request.args and request.args["status"]:
            query = query.filter(Customers.status == request.args["status"].upper())
        else:
            query = query.filter(Customers.status != "ARCHIVED")

        if "is_individual" in request.args:
            if str2bool(request.args["is_individual"]) == True:
                query = query.filter(Customers.is_individual == True)
            elif str2bool(request.args["is_individual"]) == False:
                query = query.filter(Customers.is_individual == False)

        if limit:
            if offset:
                customers = query.order_by(order).limit(limit).offset(offset).all()
            else:
                customers = query.order_by(order).limit(limit).all()
        else:
            customers = query.order_by(order).all()
    except:
        if not isDevEnv():
            errorLogger.error(
                "Error 500 : Internal Server Error - error filtering entities"
            )
            return (
                jsonify({"msg": "Internal Server Error - error executing query"}),
                500,
            )

    count_entities = query.count()

    if "/select" in request.path:
        return jsonify(customers_list_schema.dump(customers)), 200
    else:
        if currentUser["role"] in ("SUPERADMIN", "ADMIN"):
            errorLogger.info("List " + str(len(customers)) + " customers")
            return (
                jsonify(
                    {
                        "customers": customers_schema.dump(customers),
                        "count": count_entities,
                    }
                ),
                200,
            )
        else:
            return jsonify({"msg": "Forbidden"}), 403


@customers.route("/<int:id>", methods=["GET"])
@jwt_required()
def getById(id):
    """
    Show customer's information with his ID
    ---
    tags:
      - customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Customer's information
      403:
        description: Forbidden
      404:
        description: Not found
    """
    errorLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    customer = Customers.query.get(id)

    if (
        currentUser["role"] in ("SUPERADMIN", "ADMIN")
        or currentUser["user_id"] == customer.user_id
    ):
        if customer is not None:
            return jsonify(customer_schema.dump(customer)), 200
        else:
            return jsonify({"msg": "Not Found"}), 404
    else:
        return jsonify({"msg": "Forbidden"}), 403


@customers.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a customer
    ---
    tags:
      - customers
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - name
            - status
            - is_individual
            - office_address
            - office_postal_code
            - office_city
          properties:
            user_id:
              type: integer
              description: ID of the user who manage the customer
            status:
              type: string
              description: Status of the customer ['PREPARATION', 'STEP_1', 'STEP_2', 'END_MISSION', 'INACTIVE', 'ARCHIVED']
            name:
              type: string
              description: name of the customer
            is_individual:
              type: boolean
              description: If the customer is a particular (YES) or a company (NO)
            siret:
              type: string
              description: SIRET of the customer
            naf_code:
              type: string
              description: NAF code of the customer
            tva_code:
              type: string
              description: TVA code of the customer
            office_phone:
              type: string
              description: phone of the customer
            office_address:
              type: string
              description: office address of the customer
            office_address_comp:
              type: string
              description: office address complementary of the customer
            office_postal_code:
              type: string
              description: postal code of the customer
            office_city:
              type: string
              description: office city of the customer
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
    errorLogger.info(request.path + " POST")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Get Body of request
    form = request.json
    fieldsMissing = []

    if currentUser["role"] in ("SUPERADMIN"):
        if (
            "name" in form
            and form["name"]
            and "status" in form
            and form["status"]
            and "is_individual" in form
            and "office_address" in form
            and form["office_address"]
            and "office_postal_code" in form
            and form["office_postal_code"]
            and "office_city" in form
            and form["office_city"]
        ):
            if "user_id" in form and form["user_id"]:
                user = Users.query.get(form["user_id"])
                if user:
                    user_id = user.id
                else:
                    return jsonify({"msg": "Not Found : User"}), 404
            else:
                user_id = currentUser["user_id"]

            if "is_individual" in form and form["is_individual"] == True:
                # case of particular
                form["siret"] = None
                form["naf_code"] = None
                form["tva_code"] = None
            elif "is_individual" in form and form["is_individual"] == False:
                # case of company
                if (
                    "siret" not in form
                    or form["siret"] == ""
                    or "naf_code" not in form
                    or form["naf_code"] == ""
                    or "tva_code" not in form
                    or form["tva_code"] == ""
                ):
                    if "siret" not in form or form["siret"] == "":
                        fieldsMissing.append("siret")
                    if "naf_code" not in form or form["naf_code"] == "":
                        fieldsMissing.append("naf_code")
                    if "tva_code" not in form or form["tva_code"] == "":
                        fieldsMissing.append("tva_code")
                    return (
                        jsonify(
                            {
                                "msg": "Bad Request : not enought datas missing for Customer Company ["
                                + ",".join(fieldsMissing)
                                + "]"
                            }
                        ),
                        400,
                    )
            else:
                return (
                    jsonify(
                        {
                            "msg": "Bad Request : not enought datas missing [is_individual]"
                        }
                    ),
                    400,
                )
        else:
            if "is_individual" not in form:
                fieldsMissing.append("is_individual")
            if "name" not in form or form["name"] == "":
                fieldsMissing.append("name")
            if "status" not in form or form["status"] == "":
                fieldsMissing.append("status")
            if "office_address" not in form or form["office_address"] == "":
                fieldsMissing.append("office_address")
            if "office_postal_code" not in form or form["office_postal_code"] == "":
                fieldsMissing.append("office_postal_code")
            if "office_city" not in form or form["office_city"] == "":
                fieldsMissing.append("office_city")
            errorLogger.error(
                "Bad Request : not enought datas missing for Customer ["
                + ",".join(fieldsMissing)
                + "]"
            )
            return (
                jsonify(
                    {
                        "msg": "Bad Request : not enought datas missing for Customer ["
                        + ",".join(fieldsMissing)
                        + "]"
                    }
                ),
                400,
            )

        if "office_phone" not in form:
            form["office_phone"] = None
        if "office_address_comp" not in form:
            form["office_address_comp"] = None

        newEntity = Customers(
            date_create=datetime.datetime.utcnow().replace(microsecond=0),
            user_id=user_id,
            name=form["name"],
            status=form["status"],
            is_individual=form["is_individual"],
            siret=form["siret"],
            tva_code=form["tva_code"],
            office_phone=form["office_phone"],
            office_address=form["office_address"],
            office_address_comp=form["office_address_comp"],
            office_postal_code=form["office_postal_code"],
            office_city=form["office_city"],
        )

        try:
            db.session.add(newEntity)
            db.session.commit()

            return jsonify({"msg": "OK", "id": newEntity.id}), 200
        except Exception as err:
            error_str = " ".join(str(err).split())
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


@customers.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def patchById(id):
    """
    Patch a customer
    ---
    tags:
      - customers
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
            user_id:
              type: integer
              description: ID of the user who manage the customer
            status:
              type: string
              description: Status of the customer ['PREPARATION', 'STEP_1', 'STEP_2', 'END_MISSION', 'INACTIVE', 'ARCHIVED']
            name:
              type: string
              description: name of the customer
            is_individual:
              type: boolean
              description: If the customer is a particular (YES) or a company (NO)
            siret:
              type: string
              description: SIRET of the customer
            tva_code:
              type: string
              description: TVA code of the customer
            office_phone:
              type: string
              description: phone of the customer
            office_address:
              type: string
              description: office address of the customer
            office_address_comp:
              type: string
              description: office address complementary of the customer
            office_postal_code:
              type: string
              description: postal code of the customer
            office_city:
              type: string
              description: office city of the customer
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
    errorLogger.info(request.path + " PATCH")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Get Body of request
    form = request.json
    customer = Customers.query.get(id)

    if customer is not None:
        if currentUser["role"] in ("SUPERADMIN"):
            if "user_id" in form and form["user_id"]:
                user = Users.query.get(form["user_id"])
                if user:
                    customer.user_id = user.id
                else:
                    return jsonify({"msg": "Not Found : User"}), 404
            if "name" in form and form["name"]:
                customer.name = form["name"]
            if "status" in form and form["status"]:
                customer.status = form["status"]
                if customer.status == "ARCHIVED":
                    customer.date_archived = datetime.datetime.now()
            if "is_individual" in form:
                if str2bool(form["is_individual"]) == True:
                    customer.is_individual = True
                elif str2bool(form["is_individual"]) == False:
                    customer.is_individual = False
            if "siret" in form and form["siret"]:
                customer.siret = form["siret"]
            if "tva_code" in form and form["tva_code"]:
                customer.tva_code = form["tva_code"]
            if "office_phone" in form and form["office_phone"]:
                customer.office_phone = form["office_phone"]
            if "office_address" in form and form["office_address"]:
                customer.office_address = form["office_address"]
            if "office_address_comp" in form and form["office_address_comp"]:
                customer.office_address_comp = form["office_address_comp"]
            if "office_postal_code" in form and form["office_postal_code"]:
                customer.office_postal_code = form["office_postal_code"]
            if "office_city" in form and form["office_city"]:
                customer.office_city = form["office_city"]

            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Forbidden"}), 403
    else:
        return jsonify({"msg": "Not Found : Customer"}), 404


@customers.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete a customer
    ---
    tags:
      - customers
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
    errorLogger.info(request.path + " DELETE")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    if "role" in currentUser and currentUser["role"] in ("SUPERADMIN"):
        customer = Customers.query.get(id)

        if customer:
            if customer.status == "ARCHIVED":
                try:
                    errorLogger.info(
                        "...delete Cascade for Customer " + str(customer.id) + "..."
                    )
                    documents = (
                        Documents.query.join(Documents.customer)
                        .filter(Customers.id == customer.id)
                        .all()
                    )

                    if documents:
                        for document in documents:
                            errorLogger.info(
                                "Deleting Document " + str(document.id) + "..."
                            )
                            db.session.delete(document)

                    contacts = (
                        Contacts.query.join(Contacts.customer)
                        .filter(Customers.id == customer.id)
                        .all()
                    )

                    if contacts:
                        for contact in contacts:
                            errorLogger.info(
                                "Deleting Contact " + str(contact.id) + "..."
                            )
                            db.session.delete(contact)

                    customer_name = customer.name

                    errorLogger.info("Deleting Customer " + str(customer.id) + "...")
                    db.session.delete(customer)
                    db.session.commit()

                    # notify SUPERADMINS & ADMINS
                    users = Users.query.join(Users.authentication).filter(
                        Authentications.role.in_(["SUPERADMIN", "ADMIN"])
                    )

                    user_deleter = Users.query.filter(
                        Users.id == currentUser["user_id"]
                    ).first()

                    newNotification = Notifications(
                        date_create=datetime.datetime.utcnow().replace(microsecond=0),
                        title="Suppression d'utilisateur",
                        content="Le client "
                        + customer_name
                        + " a été définitivement supprimé  par "
                        + user_deleter.firstname
                        + " "
                        + user_deleter.lastname,
                        type="ALERT",
                    )
                    errorLogger.info("Adding Notification")
                    db.session.add(newNotification)
                    db.session.commit()

                    for user in users:
                        newNotificationUser = NotificationsUsers(
                            notification_id=newNotification.id,
                            user_id=user.id,
                            is_viewed=False,
                        )
                        errorLogger.info(
                            "Adding Notification to user : "
                            + user.firstname
                            + " "
                            + user.lastname
                        )
                        db.session.add(newNotificationUser)
                        db.session.commit()

                    return jsonify({"msg": "OK"}), 200
                except Exception as err:
                    db.session.rollback()
                    if not isDevEnv():
                        return jsonify({"msg": "Internal Server Error"}), 500
                    else:
                        print(err)
            else:
                has_right = False
                errorLogger.info(customer.name + " is not archived")
                return (customer.name + " is not archived"), 500
                if customer.status == "ARCHIVED":
                    has_right = True

        else:
            return jsonify({"msg": "Not Found"}), 404
    else:
        return (
            jsonify({"msg": "Forbidden", "has_right": False}),
            403,
        )


@customers.route("/export", methods=["GET"])
@jwt_required()
def exportCustomers():
    """
    Export customers
    ---
    tags:
      - customers
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
        name: name
        schema:
          type: string
        description: name of the customer
      - in: query
        name: status
        schema:
          type: string
        description: status of the customer [PREPARATION, STEP_1, STEP_2, END_MISSION, INACTIVE, ARCHIVED]
      - in: query
        name: is_individual
        schema:
          type: boolean
        description: if the customer is an individual or a company
    responses:
      200:
        description: Export customers
      403:
        description: Forbidden
      500:
        description: Internal Server Error
    """
    errorLogger.info(request.path + " GET")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    if currentUser["role"] in ("SUPERADMIN"):
        query = Customers.query
        order = asc("name")

        if "order_by" in request.args and "order_dir" in request.args:
            order = (
                asc(request.args["order_by"])
                if request.args["order_dir"] == "asc"
                else desc(request.args["order_by"])
            )

        try:
            if "name" in request.args and request.args["name"]:
                query = query.filter(
                    Customers.name.ilike(
                        "%" + escapeForDBFilter(request.args["name"]) + "%"
                    )
                )
            if "status" in request.args and request.args["status"]:
                query = query.filter(Customers.status == request.args["status"].upper())
            else:
                query = query.filter(Customers.status != "ARCHIVED")

            if "is_individual" in request.args:
                if str2bool(request.args["is_individual"]) == True:
                    query = query.filter(Customers.is_individual == True)
                elif str2bool(request.args["is_individual"]) == False:
                    query = query.filter(Customers.is_individual == False)

            count_entities = query.count()
            customers = query.order_by(order).all()

            name_filter = ""
            if "status" in request.args:
                name_filter += request.args["status"].lower() + "_"
            if "is_individual" in request.args:
                if str2bool(request.args["is_individual"]) == True:
                    name_filter += "individual_"
                elif str2bool(request.args["is_individual"]) == False:
                    name_filter += "company_"

            name_export = (
                "clients_"
                + name_filter
                + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                + ".xlsx"
            )
            path_file = environ.get("PATH_GENERATED_FILES") + "csv/" + name_export

            workbook = xlsxwriter.Workbook(path_file)
            worksheet = workbook.add_worksheet("Liste des Clients")

            cellsFormats = getXlsxCellsFormat(workbook)

            columns = [
                "ID",
                "Nom",
                "Utilisateur lié",
                "Date de création",
                "Date d'archivage",
                "Statut",
                "Code Interne",
                "SIRET",
                "Code TVA",
                "NAF Code",
                "Particulier ?",
                "Secteur d'activité",
                "Téléphone",
                "Adresse",
                "Complément d'adresse",
                "Code postal",
                "Ville",
            ]

            row = 1
            col = 0

            for item in columns:
                worksheet.write(0, col, item, cellsFormats["header_cell_format"])
                col += 1

            for customer in customers:
                if customer.status == "PREPARATION":
                    status = "Mission en préparation"
                elif customer.status == "STEP_1":
                    status = "Phase 1"
                elif customer.status == "STEP_2":
                    status = "Phase 2"
                elif customer.status == "END_MISSION":
                    status = "Mission terminée"
                elif customer.status == "INACTIVE":
                    status = "Pas de mission en cours"
                else:
                    status = "Archivé"

                if customer.user:
                    user_linked = customer.user.firstname + " " + customer.user.lastname
                else:
                    user_linked = ""

                col = 0
                worksheet.write(
                    row, col, customer.id, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, customer.name, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, user_linked, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, customer.date_create, cellsFormats["date_cell_format"]
                )
                col += 1
                worksheet.write(
                    row,
                    col,
                    customer.date_archived if customer.date_archived else "",
                    cellsFormats["date_cell_format"],
                )
                col += 1
                worksheet.write(row, col, status, cellsFormats["default_cell_format"])
                col += 1
                worksheet.write(
                    row, col, customer.siret, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row, col, customer.tva_code, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row,
                    col,
                    "OUI" if customer.is_individual else ("NON"),
                    cellsFormats["default_cell_format"],
                )
                col += 1
                worksheet.write(
                    row, col, customer.office_phone, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(
                    row,
                    col,
                    customer.office_address,
                    cellsFormats["default_cell_format"],
                )
                col += 1
                worksheet.write(
                    row,
                    col,
                    customer.office_address_comp,
                    cellsFormats["default_cell_format"],
                )
                col += 1
                worksheet.write(
                    row,
                    col,
                    customer.office_postal_code,
                    cellsFormats["default_cell_format"],
                )
                col += 1
                worksheet.write(
                    row, col, customer.office_city, cellsFormats["default_cell_format"]
                )
                col += 1
                worksheet.write(row, col, cellsFormats["default_cell_format"])
                col += 1

                row += 1

            worksheet.write(row + 1, 0, "Nombre :", cellsFormats["header_cell_format"])
            worksheet.write(
                row + 1, 1, len(customers), cellsFormats["default_cell_format"]
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
                        "nb_datas": len(customers),
                        "data": str(data),
                    }
                ),
                200,
            )

        except Exception as err:
            # delete file if created
            try:
                os.remove(path_file)
            except:
                errorLogger.info("No need to delete export file")
            error_str = " ".join(str(err).split())
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
