from os import environ
from app import db
from sqlalchemy.orm import backref

schema = environ.get("BDD_CONFIG_SCHEMA")


class Authentications(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    status = db.Column(db.String)
    role = db.Column(db.String)

    # objects back_populates
    user = db.relationship(
        "Users",
        back_populates="authentication",
        cascade="save-update, merge, delete",
        passive_deletes=False,
    )

    def __str__(self):
        return (
            "<Authentications id="
            + str(self.id)
            + ' email="'
            + self.email
            + '" status='
            + self.status
            + ' role="'
            + self.role
            + '">'
        )

class Documents(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_create = db.Column(db.Date)
    type = db.Column(db.String)
    title = db.Column(db.String)
    file_name = db.Column(db.String)
    data = db.Column(db.String)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey(schema + ".users.id"))

    # objects links
    user = db.relationship("Users", foreign_keys=user_id)


    def __str__(self):
        return (
            "<Documents id="
            + str(self.id)
            + ' title="'
            + self.title
            + '" type="'
            + self.type
            + '">'
        )
    
class Users(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String)
    date_archived = db.Column(db.Date)
    lastname = db.Column(db.String)

    # foreign keys
    authentication_id = db.Column(
        db.Integer, db.ForeignKey(schema + ".authentications.id", ondelete="CASCADE")
    )
    # objects links
    authentication = db.relationship(
        "Authentications", back_populates="user", foreign_keys=authentication_id
    )

    def __str__(self):

        return (
            "<Users id="
            + str(self.id)
            + ' firstname="'
            + self.firstname
            + '" lastname="'
            + str(self.lastname)
            + ">"
        )


class Projects(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_create = db.Column(db.Date)
    name = db.Column(db.String)
    bbox = db.Column(db.String)
    nb_plaques_h = db.Column(db.Integer)
    nb_plaques_v = db.Column(db.Integer)
    ratio = db.Column(db.Integer)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey(schema + ".users.id"))
    model_id = db.Column(db.Integer, db.ForeignKey(schema + ".documents.id"))
    csv_id = db.Column(db.Integer, db.ForeignKey(schema + ".documents.id"))

    # Object links 
    user = db.relationship("Users", foreign_keys=user_id)
    model = db.relationship("Documents", foreign_keys=model_id, viewonly=True)
    csv = db.relationship("Documents", foreign_keys=csv_id, viewonly=True)

    def __str__(self):
        return (
            "<Project id="
            + str(self.id)
            + ' date_create="'
            + str(self.date_create)
            + '" name="'
            + str(self.name)
            + '" bbox="'
            + str(self.bbox)
            + '" nb_plaques_h="'
            + str(self.nb_plaques_h)
            + '" nb_plaques_v="'
            + str(self.nb_plaques_v)
            + '" ratio="'
            + str(self.ratio)
            + '" user_id="'
            + str(self.user_id)
            + '" model_id="'
            + str(self.model_id)
            + '" csv_id="'
            + str(self.csv_id)
            + '">'
        )


class Datas(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    service = db.Column(db.String)
    url = db.Column(db.String)
    layername = db.Column(db.String)
    srsname = db.Column(db.String)
    style = db.Column(db.String)
    version = db.Column(db.String)
    only_url = db.Column(db.Boolean, nullable=True, default=False)

    # foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey(schema + ".projects.id"))

    def __str__(self):
        return (
            "<Project id="
            + str(self.id)
            + ' name="'
            + self.name
            + '" service="'
            + str(self.service)
            + '" url="'
            + str(self.url)
            + '" layername="'
            + str(self.layername)
            + '" srsname="'
            + str(self.srsname)
            + '" style="'
            + str(self.style)
            + '" version="'
            + str(self.version)
            + '" only_url="'
            + str(self.only_url)
            + '" project_id="'
            + str(self.project_id)
            + '">'
        )
