from app.utils.constants import *
from app.utils.methods import *
import app
from app import db, infoLogger, errorLogger
from app.models import Datas, Projects
from app.schemas import DatasSchema
from os import environ
from os.path import basename
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from werkzeug.local import LocalProxy

debug_mode = environ.get("DEBUG_MODE")

# model import
data_schema = DatasSchema()
datas_schema = DatasSchema(many=True)

# Create Blueprint & get logger
datas = Blueprint("datas", __name__)
logger = LocalProxy(lambda: current_app.logger)



@datas.before_request
def before_request_func():
    current_app.logger.name = "datas"

@datas.route("", methods=["GET"])
@jwt_required()
def listAll():
    """
    List all Datas
    ---
    tags:
      - Datas
    security:
      - Bearer: []
    parameters:
      - in: query
        name: project_id
        schema:
          type: integer
        description: datas of the selected project using it's ID  
    responses:
      200:
        description: List all datas of a connected user
      500:
        description: Internal Server Error
    """
    currentUser = get_jwt_identity()
    infoLogger.info(f"{request.method} → {request.path}")
    if 'project_id' in request.args:
        project = Projects.query.filter_by(id=request.args['project_id']).first()
        if project:
          if project.user_id == currentUser['id']:
              filtered_data = Datas.query.filter_by(project_id=request.args['project_id']).all()
              if len(filtered_data) == 0:
                return jsonify({'msg': "This project has no data"}), 400
              
              infoLogger.info("List " + str(len(filtered_data)) + " Datas")
              return jsonify(datas_schema.dump(filtered_data)), 200
          else: 
              return jsonify({'msg': "Forbidden"}), 403
        else:
            return jsonify({'msg': "Project Doesn't Exist"}), 400
    else:
        datas = Datas.query.all()

        infoLogger.info("List " + str(len(datas)) + " Datas")
        return jsonify(datas_schema.dump(datas)), 200

@datas.route("<int:id>", methods=["GET"])
def listById(id):
    """
      Get Datas by ID 
    ---
    tags:
      - Datas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Datas listed
      500:
        description: Error during the process
      404:
        description: User not found
    """
    infoLogger.info(f"{request.method} → {request.path}")

    project = (
        Datas.query.filter_by(id=id).first()
    )

    if project:
        return jsonify(data_schema.dump(project)), 200
    else:
        errorLogger.error("No datas found with this id " + str(id))
        return jsonify({"msg": "No datas found"}), 404
    
@datas.route("", methods=["POST"])
@jwt_required()
def create():
    """
    Create a new data
    ---
    tags:
      - Datas
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required:
            - name
            - service
            - url
            - layername
            - srsname
            - style
            - version
            - only_url
            - project_id
          properties:
            name:
              type: string
              description: name of the selected zone
            service:
              type: string
              description: the used service
            url:
              type: string
              description: the used url
            layername:
              type: string
              description: the used layername
            srsname:
              type: string
              description: the used srs
            style:
              type: string
              description: the used style
            version:
              type: string
              description: the used version
            only_url:
              type: boolean
              description: False by default.
              default: false
            project_id:
              type: integer
              description: the linked project_id
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

    # Access the identity of the current user with get_jwt_identity
    currentUser = get_jwt_identity()
    if 'project_id' in form and form['project_id'] != 0:
      project = Projects.query.filter_by(id=form['project_id']).first()
      if project:
        if project.user_id == currentUser["id"]:
          if form['only_url'] == True:
            if 'name' in form and 'url' in form:
                newdata = Datas(
                name=form['name'],
                url=form['url'],
                project_id=form['project_id'],
                only_url=form['only_url']
                )
                db.session.add(newdata)
                db.session.commit()
                return jsonify({'msg': "OK", 'id': newdata.id}), 200
            else:
                return jsonify({'msg': "Name & url are required when it's URL only"}), 404
          else:
              if 'name' in form and 'url' in form and 'service' in form and 'layername' in form and 'srsname' in form and 'style' in form and 'version' in form:
                newdata = Datas(
                  name=form['name'],
                  url=form['url'],
                  service=form['service'],
                  layername=form['layername'],
                  srsname=form['srsname'],
                  style=form['style'],
                  version=form['version'],
                  project_id=form['project_id']
                )
                db.session.add(newdata)
                db.session.commit()
                return jsonify({'msg': "OK", 'id': newdata.id}), 200
              else:
                  return jsonify({'msg': 'Missing Parameters'}), 400
        else:
            return jsonify({'msg': "Forbidden"}), 403
      else:
          return jsonify({'msg': "Project with ID " + str(form['project_id']) + " doesn't exist"}), 404
    else:
      return jsonify({'msg': "project_id is required"}), 404
    


@datas.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def updateById(id):
    """
    Update a data
    ---
    tags:
      - Datas
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
            - service
            - url
            - layername
            - srsname
            - style
            - version
            - only_url
            - project_id
          properties:
            name:
              type: string
              description: name of the selected zone
            service:
              type: string
              description: the used service
            url:
              type: string
              description: the used url
            layername:
              type: string
              description: the used layername
            srsname:
              type: string
              description: the used srs
            style:
              type: string
              description: the used style
            version:
              type: string
              description: the used version
            only_url:
              type: boolean
              description: False by default.
              default: false
            project_id:
              type: integer
              description: the linked project_id
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
    currentUser = get_jwt_identity()
    form = request.json
    data = Datas.query.get(id)
    project = Projects.query.filter_by(id=data.project_id).first()
    if project:
        if project.user_id == currentUser["id"]:
          if data:
            if data.only_url == True:
                print("here 1")
                if 'name' in form:
                    data.name = form['name']
                if 'url' in form:
                    data.url = form['url']
                if 'only_url' in form:
                    data.only_url = form['only_url']
                db.session.commit()
                return jsonify({'msg': 'OK'}), 200
            else:
                if 'name' in form:
                    data.name = form['name']
                if 'url' in form:
                    data.url = form['url']
                if 'service' in form:
                    data.service = form['service']
                if 'layername' in form:
                    data.layername = form['layername']
                if 'srsname' in form:
                    data.srsname = form['srsname']
                if 'style' in form:
                    data.style = form['style']
                if 'version' in form:
                    data.version = form['version']
                if 'only_url' in form:
                    data.only_url = form['only_url']
                # if 'project_id' in form:
                #     data.project_id = form['project_id'] -> For the moment I won't allow to change the Project_ID
                db.session.commit()
                return jsonify({'msg': 'OK'}), 200
          else:
              return jsonify({'msg': "Data with ID " + id + " Doesn't Exist"}), 404
        else:
              return jsonify({'msg': "Forbidden"}), 401
    else:
        return jsonify({'msg': "There is no project linked to a data with the ID : " + str(id)}), 404
    


@datas.route("/<int:id>", methods=["DELETE"])
@jwt_required()

def deleteById(id):
  """
  Delete a data
  ---
  tags:
    - Datas
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

  currentUser = get_jwt_identity()

  data = Datas.query.get(id)
  if data:
    project = Projects.query.filter_by(id=data.project_id).first()
    if project:
        if project.user_id == currentUser["id"]:
          has_access = True
          if has_access:
            db.session.delete(data)
            db.session.commit()
            return jsonify({'msg': 'OK'}), 200
        else:
          return jsonify({'msg': "Forbidden"}), 401
    else:
      return jsonify({'msg': 'Project of this data Not Found'}), 404
  else:
    return jsonify({'msg': 'Data Not Found'}), 404