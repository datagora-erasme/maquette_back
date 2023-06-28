from app import db, infoLogger, errorLogger
from app.models import Contacts, Customers, CustomersContacts
from app.schemas import ContactSchema
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.local import LocalProxy

# model import
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

# Utils import
from app.utils.methods import *
from app.utils.constants import *


# Create Blueprint & get logger
customers_contacts = Blueprint("customers_contacts", __name__)
logger = LocalProxy(lambda: current_app.logger)


@customers_contacts.before_request
def before_request_func():
    current_app.logger.name = "customers_contacts"


@customers_contacts.route("customers", methods=["POST"])
@jwt_required()
def create():
    """
    Create a Customer's contact
    ---
    tags:
      - contacts
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - customer_id
            - firstname
            - lastname
            - email
            - job_title
          properties:
            customer_id:
              type: integer
              description: ID of the Customer for the contact
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
    infoLogger.info(request.path + " POST")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # Get Body of request
    form = request.json

    if "role" in currentUser and currentUser["role"] in ("SUPERADMIN"):
        # nullable inputs
        if "phone" not in form or ("phone" in form and form["phone"] == None):
            form["phone"] = None
        elif "phone" in form and len(form["phone"]) == 0:
            form["phone"] = None

        if (
            "customer_id" in form
            and form["customer_id"]
            and "firstname" in form
            and form["firstname"]
            and "lastname" in form
            and form["lastname"]
            and "email" in form
            and form["email"]
            and "job_title" in form
            and form["job_title"]
        ):
            customer = Customers.query.get(form["customer_id"])

            if customer:
                try:
                    newContact = Contacts(
                        date_create=datetime.datetime.utcnow().replace(microsecond=0),
                        firstname=form["firstname"],
                        lastname=form["lastname"],
                        email=form["email"],
                        job_title=form["job_title"],
                        phone=form["phone"],
                    )

                    db.session.add(newContact)
                    db.session.commit()

                    newCustomerContact = CustomersContacts(
                        customer_id=customer.id, contact_id=newContact.id
                    )

                    db.session.add(newCustomerContact)
                    db.session.commit()

                    return jsonify({"msg": "OK", "id": newContact.id}), 200
                except Exception as err:
                    db.session.rollback()
                    error_str = " ".join(str(err).split())
                    errorLogger.error(error_str)
                    if isDevEnv():
                        return (
                            jsonify(
                                {"msg": "Internal Server Error", "error": error_str}
                            ),
                            500,
                        )
                    else:
                        return jsonify({"msg": "Internal Server Error"}), 500
            else:
                return jsonify({"msg": "Not Found : Customer"}), 404
        else:
            return jsonify({"msg": "Internal Server Error : not enough datas"}), 500
    else:
        return jsonify({"msg": "Forbidden"}), 403
