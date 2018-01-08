import unittest

from stackcite.users import testing


class CreateRequestTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_create_request_without_auth_key(self):
        from .. import utils
        request = utils.create_request()
        headers = request.headers
        with self.assertRaises(KeyError):
            headers['Authorization']

    def test_create_request_with_auth_key(self):
        from .. import utils
        key = 'key TEST_KEY'
        request = utils.create_request(key)
        headers = request.headers
        result = headers['Authorization']
        self.assertEqual(result, key)


class CreateUserTests(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()

    def test_create_user_does_not_save_user(self):
        from .. import utils
        test_email = 'test@email.com'
        utils.create_user(test_email, 'T3stPa$$word', save=False)
        from stackcite.users import models
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.User.objects.get(email=test_email)

    def test_create_user_saves_user(self):
        from .. import utils
        test_email = 'test@email.com'
        utils.create_user(test_email, 'T3stPa$$word', save=True)
        from stackcite.users import models
        import mongoengine
        try:
            models.User.objects.get(email=test_email)
        except mongoengine.DoesNotExist as err:
            self.fail(msg=err)


class CreateAuthTokenTests(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()

    def test_create_auth_token_does_not_save_user(self):
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        from .. import utils
        utils.create_auth_token(user)
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.AuthToken.objects.get(_user=user)

    def test_create_auth_token_saves_user(self):
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        from .. import utils
        utils.create_auth_token(user, save=True)
        from stackcite.users import models
        import mongoengine
        try:
            models.AuthToken.objects.get(_user=user)
        except mongoengine.DoesNotExist as err:
            self.fail(msg=err)


class CreateConfTokenTests(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()

    def test_create_conf_token_does_not_save_user(self):
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        from .. import utils
        utils.create_conf_token(user)
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.ConfirmToken.objects.get(_user=user)

    def test_create_conf_token_saves_user(self):
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        from .. import utils
        utils.create_conf_token(user, save=True)
        from stackcite.users import models
        import mongoengine
        try:
            models.ConfirmToken.objects.get(_user=user)
        except mongoengine.DoesNotExist as err:
            self.fail(msg=err)
