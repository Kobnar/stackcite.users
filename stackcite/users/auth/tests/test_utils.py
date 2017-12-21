import unittest

from stackcite.api import testing


class GenKeyTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_returns_56_char_key(self):
        from .. import utils
        result = utils.gen_key()
        self.assertEqual(56, len(result))


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
        from pyramid.testing import DummyRequest
        from ..utils import get_token
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        result = get_token(request)
        self.assertEqual(self.token, result)

    def test_invalid_key_returns_none(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_token
        request = DummyRequest()
        request.authorization = 'Key', 'invalid_key'
        result = get_token(request)
        self.assertIsNone(result)

    def test_invalid_auth_type_returns_none(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_token
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Invalid', key
        request.token = get_token(request)
        result = get_token(request)
        self.assertIsNone(result)

    def test_basic_auth_type_returns_none(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_token
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Basic', key
        result = get_token(request)
        self.assertIsNone(result)

    def test_deleted_user_does_not_raise_exception(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_token
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        self.user.delete()
        from mongoengine import InvalidDocumentError
        try:
            get_token(request)
        except InvalidDocumentError as err:
            msg = 'Unexpected exception raised: {}'.format(err)
            self.fail(msg=msg)


class GetUserIntegrationTestCase(AuthUtilsBaseIntegrationTestCase):

    def test_get_user_returns_correct_user(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_user
        key = self.token.key
        request = DummyRequest()
        request.authorization = 'Key', key
        request.token = self.token
        result = get_user(request)
        self.assertEqual(self.user, result)


class GetGroupsIntegrationTestCase(AuthUtilsBaseIntegrationTestCase):

    def test_get_groups_returns_groups(self):
        from pyramid.testing import DummyRequest
        from ..utils import get_user, get_groups
        expected = self.user.groups
        user_id = self.user.id
        request = DummyRequest()
        request.user = self.user
        result = get_groups(user_id, request)
        self.assertEqual(expected, result)
