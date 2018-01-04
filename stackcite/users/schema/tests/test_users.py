import unittest

from stackcite.api import testing


class UserSchemaTests(unittest.TestCase):

    def setUp(self):
        from .. import users
        self.schema = users.User()


class UserSchemaFieldTests(UserSchemaTests):

    def test_invalid_group_fails_validation(self):
        """User schema returns an error if an invalid group is set
        """
        from stackcite.api import auth
        data = {'groups': ['invalid', auth.STAFF]}
        result = self.schema.load(data).errors.keys()
        self.assertIn('groups', result)

    def test_missing_users_group_fails_validation(self):
        """User schema returns an error if a default group is missing
        """
        from stackcite.api import auth
        data = {'groups': [auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors.keys()
        self.assertIn('groups', result)

    def test_valid_groups_pass_validation(self):
        """User schema does not return an error if all groups are valid
        """
        from stackcite.api import auth
        data = {'groups': [auth.USERS, auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors.keys()
        self.assertNotIn('groups', result)

    def test_groups_optional(self):
        """User schema does not return an error if no groups are defined
        """
        result = self.schema.load({}).errors.keys()
        self.assertNotIn('groups', result)

    def test_new_password_requires_password(self):
        """User schema returns an error if new_password is set without existing password
        """
        data = {'new_password': 'N3wPa$$word'}
        result = self.schema.load(data).errors.keys()
        self.assertIn('new_password', result)


class UserSchemaCreateTests(UserSchemaTests):

    def setUp(self):
        super().setUp()
        self.schema.method = 'POST'

    def test_email_required(self):
        """User POST schema returns an error if no email is provided
        """
        data = {'password': 'T3stPa$$word'}
        result = self.schema.load(data).errors
        self.assertIn('email', result)

    def test_password_required(self):
        """User POST schema returns an error if no password is provided
        """
        data = {'email': 'test@email.com'}
        result = self.schema.load(data).errors
        self.assertIn('password', result)

    def test_invalid_group_fails_validation(self):
        """User POST schema returns an error for an invalid group
        """
        from stackcite.api import auth
        data = {'groups': ['invalid', auth.STAFF]}
        result = self.schema.load(data).errors
        self.assertIn('groups', result)

    def test_missing_users_group_fails_validation(self):
        """User POST schema returns an error if default group is missing
        """
        from stackcite.api import auth
        data = {'groups': [auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors
        self.assertIn('groups', result)

    def test_valid_groups_pass_validation(self):
        """User POST schema does not return an error if all groups are valid
        """
        from stackcite.api import auth
        data = {'groups': [auth.USERS, auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors
        self.assertNotIn('groups', result)

    def test_groups_optional(self):
        """User POST schema does not return an error if no groups are defined
        """
        result = self.schema.load({}).errors
        self.assertNotIn('groups', result)

    def test_valid_data_pass_validation(self):
        """User POST schema passes validation with valid data
        """
        from stackcite.api import auth
        data = {
            'email': 'test@email.com',
            'password': 'T3stPa$$word',
            'groups': [auth.USERS, auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors
        self.assertEqual(0, len(result))


class UserSchemaRetrieveTests(UserSchemaTests):

    def setUp(self):
        super().setUp()
        self.schema.method = 'GET'


class UserSchemaUpdateTests(UserSchemaTests):

    def setUp(self):
        super().setUp()
        self.schema.method = 'PUT'


class UserSchemaDeleteTests(UserSchemaTests):

    def setUp(self):
        super().setUp()
        self.schema.method = 'DELETE'

    def test_password_required(self):
        """User DELETE schema returns an error if no password is provided
        """
        result = self.schema.load({}).errors
        self.assertIn('password', result)
