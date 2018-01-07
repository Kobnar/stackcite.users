import unittest

from stackcite.users import testing


class AuthTokenTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..auth import AuthToken
        self.schema = AuthToken()

    def test_load_requires_key_field(self):
        """AuthToken.load() requires a key fields
        """
        result = self.schema.load({}).errors.keys()
        self.assertIn('key', result)

    def test_dumps_user_with_id(self):
        """AuthToken.dump() includes a user with an ObjectId
        """
        from bson import ObjectId
        from stackcite.users import models
        expected = str(ObjectId())
        user_data = {
            'id': expected,
            'email': 'test@email.com'}
        user = models.User(**user_data)
        token = models.AuthToken.new(user)
        result = self.schema.dump(token).data['user']['id']
        self.assertEqual(expected, result)

    def test_dumps_user_with_groups(self):
        """AuthToken.dump() includes a user with groups
        """
        from stackcite.users import models
        expected = ['users']
        user_data = {'email': 'test@email.com'}
        user = models.User(**user_data)
        user.add_group('users')
        token = models.AuthToken.new(user)
        result = self.schema.dump(token).data['user']['groups']
        self.assertEqual(expected, result)

    def test_dumps_issued(self):
        """AuthToken.dump() includes an 'issued' field
        """
        from stackcite.users import models
        from datetime import datetime
        now = datetime.utcnow()
        user = models.User(email='test@email.com')
        token = models.AuthToken(_user=user, _issued=now)
        expected = now.isoformat() + '+00:00'
        result = self.schema.dump(token).data['issued']
        self.assertEqual(expected, result)

    def test_dumps_touched(self):
        """AuthToken.dump() includes a 'touched' field
        """
        from stackcite.users import models
        from datetime import datetime
        now = datetime.utcnow()
        user = models.User(email='test@email.com')
        token = models.AuthToken(_user=user, _touched=now)
        expected = now.isoformat() + '+00:00'
        result = self.schema.dump(token).data['touched']
        self.assertEqual(expected, result)


class AuthenticateTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from ..auth import Authenticate
        self.schema = Authenticate()

    def test_email_field_required(self):
        """Authenticate.email is a required field
        """
        result = self.schema.load({}).errors.keys()
        self.assertIn('email', result)

    def test_password_field_required(self):
        """Authenticate.password is a required field
        """
        result = self.schema.load({}).errors.keys()
        self.assertIn('password', result)
