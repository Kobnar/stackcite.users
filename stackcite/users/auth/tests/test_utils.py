import unittest

from stackcite.api import testing


class GenKeyTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_returns_56_char_key(self):
        """gen_key() creates a 56 character key
        """
        from .. import utils
        result = utils.gen_key()
        self.assertEqual(56, len(result))

    def test_returns_different_key(self):
        """gen_key() returns a different key each time
        """
        from .. import utils
        first = utils.gen_key()
        second = utils.gen_key()
        self.assertNotEqual(first, second)


class AuthUtilsBaseIntegrationTestCase(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.AuthToken.drop_collection()
        self.user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        self.token = models.AuthToken.new(self.user, save=True)


class GetAuthTokenIntegrationTestCase(AuthUtilsBaseIntegrationTestCase):

    def test_get_token_returns_correct_token(self):
        """get_token() returns the correct token from request
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        result = utils.get_token(request)
        self.assertEqual(self.token, result)

    def test_invalid_key_returns_none(self):
        """get_token() returns None if key is invalid
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        request = DummyRequest()
        request.authorization = 'Key', 'invalid_key'
        result = utils.get_token(request)
        self.assertIsNone(result)

    def test_invalid_auth_type_returns_none(self):
        """get_token() returns None if auth type is invalid
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Invalid', key
        request.token = utils.get_token(request)
        result = utils.get_token(request)
        self.assertIsNone(result)

    def test_basic_auth_type_returns_none(self):
        """get_token() returns None if auth type is basic
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Basic', key
        result = utils.get_token(request)
        self.assertIsNone(result)

    def test_deleted_user_does_not_raise_exception(self):
        """get_token() does not raise exception for deleted user
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        self.user.delete()
        from mongoengine import InvalidDocumentError
        try:
            utils.get_token(request)
        except InvalidDocumentError as err:
            msg = 'Unexpected exception raised: {}'.format(err)
            self.fail(msg=msg)


class GetUserIntegrationTestCase(AuthUtilsBaseIntegrationTestCase):

    def test_get_user_returns_correct_user(self):
        """get_user() returns user associated with a request
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        request.token = self.token
        result = utils.get_user(request)
        self.assertEqual(self.user, result)

    def test_get_user_returns_none_if_token_not_set(self):
        """get_user() returns None if token is not set
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        request = DummyRequest()
        request.token = None
        result = utils.get_user(request)
        self.assertIsNone(result)


class GetGroupsIntegrationTestCase(AuthUtilsBaseIntegrationTestCase):

    def test_get_groups_returns_groups(self):
        """get_groups() returns groups associated with a matching user
        """
        from pyramid.testing import DummyRequest
        from .. import utils
        expected = self.user.groups
        user_id = self.user.id
        request = DummyRequest()
        request.user = self.user
        result = utils.get_groups(user_id, request)
        self.assertEqual(expected, result)
