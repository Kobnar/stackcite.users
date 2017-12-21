from marshmallow import Schema, fields

from stackcite.api.schema import fields as api_fields


class AuthToken(Schema):
    key = api_fields.AuthTokenKeyField(required=True)


class Authenticate(Schema):
    email = fields.Email(required=True)
    password = api_fields.PasswordField(required=True)
