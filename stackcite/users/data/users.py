import bcrypt
import mongoengine

from datetime import datetime

from stackcite.api import auth
from stackcite.api import data

from stackcite.api.data import validators

from stackcite.users import exceptions


class User(data.IDocument):
    """
    A user account.
    """

    DEFAULT_GROUPS = [auth.USERS]

    email = mongoengine.EmailField(required=True, unique=True)

    _groups = mongoengine.ListField(
        mongoengine.StringField(choices=auth.GROUP_CHOICES), db_field='groups')
    _joined = mongoengine.DateTimeField(db_field='joined', required=True)
    _confirmed = mongoengine.DateTimeField(db_field='confirmed')
    _last_login = mongoengine.DateTimeField(db_field='last_login')
    _prev_login = mongoengine.DateTimeField(db_field='prev_login')
    _salt = mongoengine.StringField(required=True)
    _hash = mongoengine.StringField(required=True)

    _validate_group = validators.GroupValidator()
    _validate_password = validators.PasswordValidator()

    @property
    def groups(self):
        return self._groups

    def add_group(self, group):
        self._validate_group(group)
        if group not in self.groups:
            self._groups.append(group)

    def remove_group(self, group):
        idx = self._groups.index(group)
        self._groups.pop(idx)

    @property
    def joined(self):
        return self._joined

    @property
    def confirmed(self):
        return self._confirmed

    def confirm(self):
        for group in self.DEFAULT_GROUPS:
            self.add_group(group)
        self._confirmed = datetime.utcnow()

    @property
    def last_login(self):
        return self._last_login

    @property
    def previous_login(self):
        return self._prev_login

    def touch_login(self):
        self._prev_login = self._last_login
        self._last_login = datetime.utcnow()
        return self.last_login

    def set_password(self, new_password):
        self._validate_password(new_password)
        self._salt = self._new_salt()
        self._hash = self._encrypt(new_password)

    def check_password(self, password):
        if self._salt and self._hash:
            self._validate_password(password)
            check = self._encrypt(password)
            return self._hash == check
        else:
            return False

    @property
    def password(self):
        return bool(self._hash and self._salt)

    @password.setter
    def password(self, value):
        self.set_password(value)

    @staticmethod
    def new(email, password, save=False):
        user = User(email=email)
        user.password = password
        if save:
            user.save(cascade=True)
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            raise exceptions.AuthenticationError()

    @staticmethod
    def _new_salt():
        return bcrypt.gensalt().decode('utf-8')

    def _encrypt(self, password):
        salt = self._salt.encode('utf-8')
        password = password.encode('utf-8')
        return bcrypt.hashpw(password, salt).decode('utf-8')

    def clean(self):
        if not self._joined:
            self._joined = datetime.utcnow()

    def _deserialize(self, data):
        if data.get('groups'):
            groups = data.pop('groups')
            for new_group in groups:
                for old_group in self.groups:
                    if old_group not in groups:
                        self.remove_group(old_group)
                if new_group not in self.groups:
                    self.add_group(new_group)
        super()._deserialize(data)
