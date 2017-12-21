from marshmallow import Schema, fields

from stackcite.api.schema import (
    fields as api_fields
)

from . import users


class ConfirmToken(Schema):
    key = api_fields.AuthTokenKeyField()
    user = fields.Nested(users.User)
    issued = fields.DateTime()


class CreateConfirmationToken(Schema):
    email = fields.Email(required=True)


class UpdateConfirmationToken(Schema):
    key = api_fields.AuthTokenKeyField(required=True)
