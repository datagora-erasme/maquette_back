from app import ma
from app.models import Users
from app.models import (
    Documents,
    Notifications,
    Avatars,
    Customers,
    Contacts,
)


class DocumentOnlySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Documents


class DocumentSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested("UserSchema", only=("id",), many=False)

    class Meta:
        fields = ("id", "title", "type", "user")


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    status = ma.Nested("NotificationUserSchema", exclude=("notification",), many=False)

    class Meta:
        model = Notifications


class AuthenticationSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(
        "UserAdminSchema",
        only=(
            "firstname",
            "lastname",
        ),
        many=True,
    )

    class Meta:
        fields = ("id", "email", "role", "status", "user")


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "authentication")


class UserListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "lastname", "firstname")


class UserAdminSchema(ma.SQLAlchemyAutoSchema):
    authentication = ma.Nested("AuthenticationSchema", exclude=("user",), many=False)

    class Meta:
        model = Users


class NotificationUserSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested("UserSchema", only=("id",), many=False)
    notification = ma.Nested("NotificationSchema", many=False)

    class Meta:
        fields = ("id", "is_viewed", "notification", "user")


class AvatarDetailsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avatars


class AvatarShortedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "type", "file_name")


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers


class CustomerListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "name")


class ContactSchema(ma.SQLAlchemyAutoSchema):
    customer = ma.Nested("CustomerSchema", only=("id", "name"))

    class Meta:
        model = Contacts
