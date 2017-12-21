from marshmallow import (
    fields,
    validates,
    validates_schema,
    ValidationError
)

from stackcite.api.schema import (
    fields as api_fields,
    schema as api_schema
)

from . import data


def _validate_default_groups(value):
    for default_group in data.User.DEFAULT_GROUPS:
        if default_group not in value:
            msg = 'Default group missing: {} not in {}'.format(
                default_group, value)
            raise ValidationError(msg)


def _validate_required_fields(data, required_fields):
    for field in required_fields:
        value = data.get(field)
        if not value:
            msg = 'Missing data for required field.'
            raise ValidationError(msg, [field])


def _validate_new_password(data):
    new_password = data.get('new_password')
    password = data.get('password')
    if new_password and not password:
        msg = 'Setting a new password requires the existing password to be set.'
        raise ValidationError(msg, ['new_password'])


def _validate_create_user(data):
    _validate_required_fields(data, ('email', 'password'))


def _validate_delete_user(data):
    _validate_required_fields(data, ('password',))


class User(api_schema.APICollectionSchema):

    id = api_fields.ObjectIdField(dump_only=True)
    email = fields.Email()
    password = api_fields.PasswordField()
    new_password = api_fields.PasswordField(load_only=True)
    groups = fields.List(api_fields.GroupField())

    @validates('groups')
    def validate_groups(self, value):
        _validate_default_groups(value)

    @validates_schema
    def validate_schema(self, data):
        _validate_new_password(data)

        if self.method is 'POST':
            _validate_create_user(data)

        elif self.method is 'DELETE':
            _validate_delete_user(data)
