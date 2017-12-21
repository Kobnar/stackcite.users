from datetime import datetime
import mongoengine
from mongoengine import context_managers

from stackcite.api import auth, data

from . import users


class TokenKeyField(mongoengine.StringField):
    """
    A randomly generated string used as an API key.
    """

    _validate_key = data.validators.KeyValidator()

    def validate(self, value):
        super().validate(value)
        try:
            self._validate_key(value)
        except data.validators.ValidationError as err:
            raise mongoengine.ValidationError(err.message)


class AuthToken(mongoengine.Document):
    """
    An API key issued when a user logs in via api. An API token is automatically
    invalidated if it has not been "touched" in more than 1 hour.
    """

    _key = TokenKeyField(
        primary_key=True, db_field='key', max_length=56)
    _user = mongoengine.CachedReferenceField(
        users.User, db_field='user', required=True, fields=('id', '_groups'))
    _issued = mongoengine.DateTimeField(db_field='issued', required=True)
    _touched = mongoengine.DateTimeField(db_field='touched', required=True)

    @classmethod
    def new(cls, user, save=False):
        token = cls(_user=user)
        if save:
            token.save()
        return token

    @property
    def key(self):
        return self._key

    @property
    def user(self):
        return self._user

    @property
    def issued(self):
        return self._issued

    @property
    def touched(self):
        return self._touched

    def touch(self):
        self._touched = datetime.utcnow()
        return self.touched

    def clean(self):
        now = self.touch()
        if not self.key:
            self._key = auth.gen_key()
            self._issued = now

    meta = {
        'indexes': [
            {
                'fields': ['_touched'],
                'expireAfterSeconds': 60*60  # 1 Hour
            }
        ]
    }

    def _serialize(self, fields):
        with context_managers.no_dereference(AuthToken):
            return {
                'key': self.key,
                'user': {
                    'id': str(self.user.id) if self.user.id else None,
                    'groups': self.user.groups
                } if self.user else {},
                'issued': str(self.issued),
                'touched': str(self.touched)
            }


class ConfirmToken(mongoengine.Document):
    """
    A one-time-use account confirmation token generated when a new user is
    created. Token will survive for a limited amount of time.
    """

    _key = TokenKeyField(
        primary_key=True, db_field='key', max_length=56)
    _user = mongoengine.CachedReferenceField(
        users.User, db_field='user', required=True, fields=('id',))
    _issued = mongoengine.DateTimeField(db_field='issued', required=True)

    @classmethod
    def new(cls, user, save=False):
        token = cls(_user=user)
        if save:
            token.save()
        return token

    @property
    def key(self):
        return self._key

    @property
    def user(self):
        return self._user

    @property
    def issued(self):
        return self._issued

    def confirm_user(self):
        self.user.confirm()
        self.user.save()
        self.delete()
        return self.user

    def clean(self):
        if not self.key:
            self._key = auth.gen_key()
            self._issued = datetime.utcnow()

    meta = {
        'indexes': [
            {
                'fields': ['_issued'],
                'expireAfterSeconds': 15*60  # 15 minutes
            }
        ]
    }

    def _serialize(self, fields):
        with context_managers.no_dereference(ConfirmToken):
            return {
                'key': self.key,
                'user': {
                    'id': str(self.user.id) if self.user.id else None,
                } if self.user else {},
                'issued': str(self.issued)
            }
