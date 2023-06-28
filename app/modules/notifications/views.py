from app.utils.constants import *
from app.utils.methods import *
import app
from app import db, infoLogger, errorLogger
from app.models import Notifications, Users, NotificationsUsers
from app.schemas import NotificationSchema, NotificationUserSchema
from os import environ
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from werkzeug.local import LocalProxy

# model import
notif_schema = NotificationSchema()
notifs_schema = NotificationSchema(many=True)
notif_user_schema = NotificationUserSchema()
notifs_user_schema = NotificationUserSchema(many=True)

# Utils import

# Create Blueprint & get logger
notifs = Blueprint("notifications", __name__)
logger = LocalProxy(lambda: current_app.logger)


@notifs.before_request
def before_request_func():
    current_app.logger.name = "notifications"


@notifs.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all notifications from connected user
    ---
    tags:
      - notifications
    security:
      - Bearer: []
    responses:
      200:
        description: List all notifications from connected user
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    # filters
    limit = None
    offset = None

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

    query = Notifications.query
    query = query.join(Notifications.status).filter(
        NotificationsUsers.user_id == currentUser["user_id"]
    )

    count_notifications = query.count()

    if limit:
        if offset:
            notifs = (
                query.order_by(desc("date_create")).limit(limit).offset(offset).all()
            )
        else:
            notifs = query.order_by(desc("date_create")).limit(limit).all()
    else:
        notifs = query.order_by(desc("date_create")).all()

    infoLogger.info("List " + str(len(notifs)) + " notifs")

    return (
        jsonify(
            {"notifications": notifs_schema.dump(notifs), "count": count_notifications}
        ),
        200,
    )


@notifs.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a new notification
    ---
    tags:
      - notifications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - label
          properties:
            title:
              type: string
              description: Title of the notification
            content:
              type: string
              description: Content of the notification
            type:
              type: string
              description: type of the notification ('ALERT', 'WARNING', 'INFO', 'SUCCESS')
            label:
              type: string
              description: Label of the notification
            link:
              type: string
              description: url of the link of the notification object
    responses:
      200:
        description: OK
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Get Body of request
    form = request.json

    if "type" in form:
        if "link" not in form:
            form["link"] = None

        newNotification = Notifications(
            date_create=datetime.datetime.utcnow(),
            title=form["title"],
            type=form["type"],
            content=form["content"],
            link=form["link"],
        )

        db.session.add(newNotification)
        db.session.commit()

        return jsonify(notif_schema.dump(newNotification)), 200
    else:
        errorLogger.error("Error 400 : not enough datas to create a notification")
        return jsonify({"msg": "Bad Request"}), 400


@notifs.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def patchById(id):
    """
    Update a notification
    ---
    tags:
      - notifications
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
              description: Title of the notification
            content:
              type: string
              description: Content of the notification
            type:
              type: string
              description: type of the notification ('ALERT', 'WARNING', 'INFO', 'SUCCESS')
            label:
              type: string
              description: Label of the notification
            link:
              type: string
              description: Link of the notification
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

    notif = Notifications.query.get(id)

    if notif:
        if currentUser["role"] == "SUPERADMIN":
            # Get Body of request
            form = request.json

            if "label" in form:
                notif.label = form["label"]
            if "link" in form:
                notif.link = form["link"]

            db.session.commit()

            return jsonify(notif_schema.dump(notif)), 200
        else:
            errorLogger.error(
                "Error 403 : do not have access to edit the match with id " + str(id)
            )
            return jsonify({"msg": "Forbidden"}), 403
    else:
        errorLogger.error("Error 404 : notification not found")
        return jsonify({"msg": "Not Found"}), 404


@notifs.route("/viewed_all", methods=["PATCH"])
@jwt_required()
def patchForAllViewed():
    """
    Set status viewed to all notifications from the user
    ---
    tags:
      - notifications
    security:
      - Bearer: []
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

    try:
        query = NotificationsUsers.query
        notifications = query.filter(
            NotificationsUsers.user_id == currentUser["user_id"]
        )

        if notifications:
            for notif in notifications:
                notif.is_viewed = True
                db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            return jsonify({"msg": "Not Found"}), 404
    except:
        return jsonify({"msg": "Internal Server Error"}), 500


@notifs.route("/<int:id>/viewed", methods=["PATCH"])
@jwt_required()
def patchForViewed(id):
    """
    Set notification as is_viewed
    ---
    tags:
      - notifications
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

    notif = (
        NotificationsUsers.query.filter(NotificationsUsers.notification_id == id)
        .filter(NotificationsUsers.user_id == currentUser["user_id"])
        .first()
    )

    if notif:
        if notif.is_viewed == False:
            notif.is_viewed = True
            db.session.commit()
            return jsonify({"msg": "OK"}), 200
        else:
            errorLogger.error("Error 403 : do not have access")
            return jsonify({"msg": "Forbidden"}), 403
    else:
        errorLogger.error("Error 404 : notification not found")
        return jsonify({"msg": "Not Found"}), 404


@notifs.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deleteById(id):
    """
    Delete a notification by his ID
    ---
    tags:
      - notifications
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
    """
    infoLogger.info(f"{request.method} → {request.path}")

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()

    notif = Notifications.query.get(id)

    if notif:
        if currentUser["role"] == "SUPERADMIN":
            db.session.delete(notif)
            db.session.commit()

            return jsonify({"msg": "OK"}), 200
        else:
            errorLogger.error("Error 403 : do not have access")
            return jsonify({"msg": "Forbidden"}), 403
    else:
        errorLogger.error("Error 404 : notification with id " + str(id) + " not found")
        return jsonify({"msg": "Not Found"}), 404
