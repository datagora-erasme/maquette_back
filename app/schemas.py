from app import ma
from app.models import Users, Projects, Datas


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


class ProjectsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Projects


class DatasSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Datas
