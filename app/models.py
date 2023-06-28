from os import environ
from app import db
from sqlalchemy.orm import backref

schema = environ.get("BDD_CONFIG_SCHEMA")


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

    # objects back_populates
    customer = db.relationship(
        "Customers",
        secondary=schema + ".customers_documents",
        back_populates="documents",
        uselist=False,
    )

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


class Authentications(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    status = db.Column(db.String)
    role = db.Column(db.String)

    # no foreign keys
    # no objects links

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


class Users(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String)
    date_archived = db.Column(db.Date)
    lastname = db.Column(db.String)
    phone = db.Column(db.String, nullable=True, default=None)

    # foreign keys
    authentication_id = db.Column(
        db.Integer, db.ForeignKey(schema + ".authentications.id", ondelete="CASCADE")
    )
    avatar_id = db.Column(
        db.Integer, db.ForeignKey(schema + ".avatars.id"), nullable=True, default=None
    )

    # objects links
    authentication = db.relationship(
        "Authentications", back_populates="user", foreign_keys=authentication_id
    )
    customers = db.relationship("Customers", back_populates="user")

    avatar = db.relationship(
        "Avatars",
        foreign_keys=avatar_id,
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=False,
    )

    # objects back_populates
    notifications = db.relationship(
        "NotificationsUsers",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=False,
    )

    def __str__(self):
        phonePart = "NULL" if (self.phone == None) else str(self.phone)

        return (
            "<Users id="
            + str(self.id)
            + ' firstname="'
            + self.firstname
            + '" lastname="'
            + str(self.lastname)
            + '" phone='
            + phonePart
            + ">"
        )


class Notifications(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_create = db.Column(db.Date)
    title = db.Column(db.String)
    type = db.Column(db.String)
    content = db.Column(db.String)
    link = db.Column(db.String, nullable=True, default=None)

    # no foreign keys

    # no objects links

    # objects back_populates
    status = db.relationship(
        "NotificationsUsers",
        back_populates="notification",
        cascade="save-update, merge, delete",
        passive_deletes=False,
        uselist=True,
    )

    def __str__(self):
        linkPart = "NULL" if (self.link == None) else self.link

        return (
            "<Notifications id="
            + str(self.id)
            + ' title="'
            + self.title
            + '" type="'
            + str(self.type)
            + '" content="'
            + str(self.content)
            + '" link="'
            + linkPart
            + '">'
        )


class NotificationsUsers(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_viewed = db.Column(db.Boolean, nullable=True, default=False)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey(schema + ".users.id"))
    notification_id = db.Column(
        db.Integer, db.ForeignKey(schema + ".notifications.id", ondelete="CASCADE")
    )

    # objects links
    user = db.relationship(
        "Users", back_populates="notifications", foreign_keys=user_id
    )

    notification = db.relationship(
        "Notifications", back_populates="status", foreign_keys=notification_id
    )

    # no objects back_populates

    def __str__(self):
        viewedStatus = "YES" if (self.is_viewed) else "NO"

        return (
            "<NotificationsUsers id="
            + str(self.id)
            + " is_viewed="
            + viewedStatus
            + ' user_id="'
            + str(self.user_id)
            + '" notification_id="'
            + str(self.notification_id)
            + '">'
        )


class Avatars(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String)
    file_name = db.Column(db.String)
    data = db.Column(db.String)

    user = db.relationship("Users", back_populates="avatar")

    def __str__(self):
        return (
            "<avatar_id="
            + str(self.id)
            + ' type="'
            + self.type
            + '" filename='
            + self.file_name
            + ' Data="'
            + self.data
            + '">'
        )


class Customers(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_create = db.Column(db.Date)
    date_archived = db.Column(db.Date)
    name = db.Column(db.String)
    status = db.Column(db.String)
    is_individual = db.Column(db.Boolean)
    siret = db.Column(db.String)
    tva_code = db.Column(db.String, nullable=True, default=None)
    office_phone = db.Column(db.String, nullable=True, default=None)
    office_address = db.Column(db.String)
    office_address_comp = db.Column(db.String, nullable=True, default=None)
    office_postal_code = db.Column(db.String)
    office_city = db.Column(db.String)

    # no foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey(schema + ".users.id"))
    # no objects links
    user = db.relationship("Users", foreign_keys=user_id, back_populates="customers")

    # objects back_populates
    contacts = db.relationship(
        "Contacts", secondary=schema + ".customers_contacts", back_populates="customer"
    )
    documents = db.relationship(
        "Documents",
        secondary=schema + ".customers_documents",
        back_populates="customer",
    )


class CustomersContacts(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey(schema + ".customers.id"))
    contact_id = db.Column(db.Integer, db.ForeignKey(schema + ".contacts.id"))

    # objects links
    customer = db.relationship("Customers", foreign_keys=customer_id, viewonly=True)
    contacts = db.relationship("Contacts", foreign_keys=contact_id, viewonly=True)

    # no objects back_populates

    def __str__(self):
        return (
            "<CustomersContacts id="
            + str(self.id)
            + " customer_id="
            + str(self.customer_id)
            + " contact_id="
            + str(self.contact_id)
            + ">"
        )


class CustomersDocuments(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey(schema + ".customers.id"))
    document_id = db.Column(db.Integer, db.ForeignKey(schema + ".documents.id"))

    # objects links
    customer = db.relationship("Customers", foreign_keys=customer_id, viewonly=True)
    documents = db.relationship("Documents", foreign_keys=document_id, viewonly=True)

    # no objects back_populates

    def __str__(self):
        return (
            "<CustomersDocuments id="
            + str(self.id)
            + " customer_id="
            + str(self.customer_id)
            + " document_id="
            + str(self.document_id)
            + ">"
        )


class Contacts(db.Model):
    __table_args__ = {"schema": schema}

    # fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_create = db.Column(db.Date)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String, nullable=True, default=None)
    job_title = db.Column(db.String, nullable=True, default=None)
    # no foreign keys
    # no objects links

    # objects back_populates
    customer = db.relationship(
        "Customers",
        secondary=schema + ".customers_contacts",
        back_populates="contacts",
        uselist=False,
    )

    def __str__(self):
        return (
            "<Contacts id="
            + str(self.id)
            + ' firstname="'
            + self.firstname
            + '" lastname="'
            + self.lastname
            + ' email="'
            + self.email
            + ' job_title="'
            + self.job_title
            + '">'
        )
