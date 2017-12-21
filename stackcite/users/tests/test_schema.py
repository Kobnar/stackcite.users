import unittest

from stackcite.users import testing


class UserSchemaTests(unittest.TestCase):

    def setUp(self):
        from .. import schema
        self.schema = schema.User()


class UserSchemaFieldTests(UserSchemaTests):

    layer = testing.layers.UnitTestLayer

    def test_invalid_group_fails_validation(self):
        """User schema returns an error if an invalid group is set
        """
        from stackcite.users import auth
        data = {'groups': ['invalid', auth.STAFF]}
        result = self.schema.load(data).errors.keys()
        self.assertIn('groups', result)

    def test_missing_users_group_fails_validation(self):
        """User schema returns an error if a default group is missing
        """
        from stackcite.users import auth
        data = {'groups': [auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors.keys()
        self.assertIn('groups', result)

    def test_valid_groups_pass_validation(self):
        """User schema does not return an error if all groups are valid
        """
        from stackcite.users import auth
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

    layer = testing.layers.UnitTestLayer

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
        from stackcite.users import auth
        data = {'groups': ['invalid', auth.STAFF]}
        result = self.schema.load(data).errors
        self.assertIn('groups', result)

    def test_missing_users_group_fails_validation(self):
        """User POST schema returns an error if default group is missing
        """
        from stackcite.users import auth
        data = {'groups': [auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors
        self.assertIn('groups', result)

    def test_valid_groups_pass_validation(self):
        """User POST schema does not return an error if all groups are valid
        """
        from stackcite.users import auth
        data = {'groups': [auth.USERS, auth.STAFF, auth.ADMIN]}
        result = self.schema.load(data).errors
        self.assertNotIn('groups', result)

    def test_groups_optional(self):
        """User POST schema does not return an error if no groups are defined
        """
        result = self.schema.load({}).errors
        self.assertNotIn('groups', result)


class UserSchemaRetrieveTests(UserSchemaTests):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        super().setUp()
        self.schema.method = 'GET'


class UserSchemaUpdateTests(UserSchemaTests):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        super().setUp()
        self.schema.method = 'PUT'


class UserSchemaDeleteTests(UserSchemaTests):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        super().setUp()
        self.schema.method = 'DELETE'

    def test_password_required(self):
        """User DELETE schema returns an error if no password is provided
        """
        result = self.schema.load({}).errors
        self.assertIn('password', result)
