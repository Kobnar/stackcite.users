from marshmallow import Schema, fields as mm_fields

from stackcite.api.schema import fields as api_fields

from . import users


class AuthToken(Schema):
    """
    An AuthToken schema for serializing and deserializing authentication tokens documents.
    """

    key = api_fields.AuthTokenKeyField(required=True)

    user = mm_fields.Nested(users.User)
    issued = mm_fields.DateTime(dump_only=True)
    touched = mm_fields.DateTime(dump_only=True)


class Authenticate(Schema):
    """
    A specific schema used to deserialize authentication data.
    """

    email = mm_fields.Email(required=True)
    password = api_fields.PasswordField(required=True)
