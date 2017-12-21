import unittest

from stackcite.users import testing


class AuthResourceIntegrationTestCase(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import data as db
        db.User.drop_collection()
        db.AuthToken.drop_collection()
        from stackcite.users import resources
        self.collection = resources.AuthResource(None, 'auth')

    def test_create_updates_last_login(self):
        """AuthResource.create() updates User.last_login with a more recent time
        """
        from stackcite.users import data as db
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user and set last_login
        user = testing.utils.create_user(email, password)
        prev_login = user.touch_login()
        user.save()
        # Wait 0.1 seconds
        import time
        time.sleep(0.001)
        # Log in user
        auth_data = {'email': email, 'password': password}
        self.collection.create(auth_data)
        # Query updated user
        user = db.User.objects.get(email=email)
        last_login = user.last_login
        login_delta = last_login - prev_login
        self.assertGreater(login_delta.microseconds, 1000)

    def test_create_raises_exception_for_unregistered_user(self):
        """AuthResource.create() raises exception for unregistered user
        """
        from mongoengine import DoesNotExist
        auth_data = {'email': 'test@email.com', 'password': 'T3stPa$$word'}
        with self.assertRaises(DoesNotExist):
            self.collection.create(auth_data)

    def test_create_raises_exception_for_wrong_password(self):
        """AuthResource.create() raises exception for wrong password
        """
        from stackcite.users import exceptions as exc
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Log in user
        auth_data = {'email': email, 'password': 'Wr0ngPa$$word'}
        with self.assertRaises(exc.AuthenticationError):
            self.collection.create(auth_data)

    def test_create_returns_user_field_on_success(self):
        """AuthResource.create() returns token with correct user email for successful login
        """
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Log in user
        auth_data = {'email': email, 'password': password}
        result = self.collection.create(auth_data).user.email
        self.assertEqual(email, result)

    def test_create_returns_token_on_success(self):
        """AuthResource.create() returns token with assigned key for successful login
        """
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Log in user
        auth_data = {'email': email, 'password': password}
        result = self.collection.create(auth_data).key
        self.assertIsNotNone(result)

    def test_retrieve_returns_token_on_success(self):
        """AuthResource.retrieve() returns the correct API token if it exists
        """
        from stackcite.users import data as db
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Make new token
        token = db.AuthToken(_user=user)
        token.save()
        result = self.collection.retrieve(token).key
        expected = token.key
        self.assertEqual(expected, result)

    def test_update_returns_token_on_success(self):
        """AuthResource.update() returns the correct API token if it exists
        """
        from stackcite.users import data as db
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Make new token
        token = db.AuthToken(_user=user)
        token.save()
        result = self.collection.update(token).key
        expected = token.key
        self.assertEqual(expected, result)

    def test_delete_none_returns_false(self):
        """AuthResource.delete() returns 'False' if given 'None'
        """
        result = self.collection.delete(None)
        self.assertFalse(result)

    def test_delete_success_returns_true(self):
        """AuthResource.delete() returns 'True' if successful
        """
        from stackcite.users import data as db
        email = 'test@email.com'
        password = 'T3stPa$$word'
        # Create user
        user = testing.utils.create_user(email, password)
        user.save()
        # Create auth token
        token = db.AuthToken(_user=user)
        token.save()
        result = self.collection.delete(token)
        self.assertTrue(result)
