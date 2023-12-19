from app.utils.constants import *
from app.utils.methods import *
import app
from app import db, infoLogger, errorLogger
from app.models import Projects
from app.schemas import ProjectsSchema
from os import environ
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from werkzeug.local import LocalProxy

# model import
project_schema = ProjectsSchema()
projects_schema = ProjectsSchema(many=True)

# Create Blueprint
projects = Blueprint("projects", __name__)



@projects.before_request
def before_request_func():
    current_app.logger.name = "projects"


@projects.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all Projects of the connected user
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: query
        name: user_id
        schema:
          type: integer
        description: user_id to use with the projects listing
    responses:
      200:
        description: List all Projects of a connected user
      500:
        description: Internal Server Error
    """
    infoLogger.info(f"{request.method} → {request.path}")

    if 'user_id' in request.args:
        filtered_projects = Projects.query.filter_by(user_id=request.args['user_id']).all()
        infoLogger.info("List " + str(len(filtered_projects)) + " Projects")
        return jsonify(projects_schema.dump(filtered_projects)), 200
    else:
        projects = Projects.query.all()
        infoLogger.info("List " + str(len(projects)) + " Projects")
        return jsonify(projects_schema.dump(projects)), 200


@projects.route("<int:id>", methods=["GET"])
def listById(id):
    """
      Get Projects by ID 
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Projects listed
      500:
        description: Error during the process
      404:
        description: User not found
    """
    infoLogger.info(f"{request.method} → {request.path}")

    project = (
        Projects.query.filter_by(id=id).first()
    )

    if project:
        return jsonify(project_schema.dump(project)), 200
    else:
        errorLogger.error("No projects found with this user id " + str(id))
        return jsonify({"msg": "No projects found"}), 404
    
@projects.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a new project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - name
            - bbox
            - nb_plaques_h
            - nb_plaques_v
            - ratio
            - model_id
            - csv_id
          properties:
            name:
              type: string
              description: name of the selected zone
            bbox:
              type: string
              description: the BBox of that selected zone
            nb_plaques_h:
              type: integer
              description: the number of horizontal plates
            nb_plaques_v:
              type: integer
              description: the number of vertical plates
            ratio:
              type: integer
              description: ratio
            model_id:
              type: integer
              description: model document
            csv_id:
              type: integer
              description: csv document
            emprise_id:
              type: integer
              description: emprise document
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

    if currentUser:
        # Get Body of request
        form = request.json
        if 'name' in form and 'bbox' in form and 'nb_plaques_h' in form and 'nb_plaques_v' in form and 'ratio' in form:
            newproject = Projects(
                date_create=datetime.datetime.utcnow(),
                user_id=currentUser['user_id'],
                name=form['name'],
                bbox=form['bbox'],
                nb_plaques_h=form['nb_plaques_h'],
                nb_plaques_v=form['nb_plaques_v'],
                ratio=form['ratio'],
                model_id=form['model_id'] if 'model_id' in form else None,
                csv_id=form['csv_id'] if 'csv_id' in form else None,
                emprise_id=form['emprise_id'] if 'emprise_id' in form else None
            )
            db.session.add(newproject)
            db.session.commit()
            return jsonify({'msg': "OK", 'id': newproject.id}), 200
        else:
            return jsonify({'msg': 'Bad Request'}), 400
    else:
        return jsonify({'msg': "Forbidden"}), 403
    


@projects.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def updateById(id):
    """
    Update a project
    ---
    tags:
      - Projects
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
            - name
            - bbox
            - nb_plaques_h
            - nb_plaques_v
            - ratio
          properties:
            name:
              type: string
              description: name of the selected zone
            bbox:
              type: string
              description: the BBox of that selected zone
            nb_plaques_h:
              type: integer
              description: the number of horizontal plates
            nb_plaques_v:
              type: integer
              description: the number of vertical plates
            ratio:
              type: integer
              description: ratio
            model_id:
              type: integer
              description: ratio
            csv_id:
              type: integer
              description: ratio
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

    form = request.json
    project = Projects.query.get(id)
    if project is not None:
        if 'name' in form:
            project.name = form['name']
        if 'bbox' in form:
            project.bbox = form['bbox']
        if 'nb_plaques_h' in form:
            project.nb_plaques_h = form['nb_plaques_h']
        if 'nb_plaques_v' in form:
            project.nb_plaques_v = form['nb_plaques_v']
        if 'ratio' in form:
            project.ratio = form['ratio']
        if 'model_id' in form:
            project.model_id = form['model_id']
        if 'csv_id' in form:
            project.csv_id = form['csv_id']
        db.session.commit()
        return jsonify({'msg': 'OK'}), 200
    else:
        return jsonify({'msg': 'Project Not Found'}), 404
    


@projects.route("/<int:id>", methods=["DELETE"])
@jwt_required()

def deleteById(id):
  """
  Delete a project
  ---
  tags:
    - Projects
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

  project = Projects.query.get(id)

  if project:
    if project.user_id == currentUser['id']:
      has_access = True
    if has_access:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'msg': 'OK'}), 200
    else:
      return jsonify({'msg': "Forbidden"}), 401
  else:
    return jsonify({'msg': 'Not Found'}), 404