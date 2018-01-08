import unittest

from stackcite.users import testing


class AuthPolicyIntegrationTests(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        from .. import policies
        self.auth_pol = policies.AuthTokenAuthenticationPolicy()
        models.User.drop_collection()
        models.AuthToken.drop_collection()
        self.user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        self.token = models.AuthToken.new(self.user, save=True)

    def test_authenticated_userid_returns_none(self):
        """AuthTokenAuthenticaitonPolicy.authenticated_userid() returns None if user.id not set
        """
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        request.user = None
        result = self.auth_pol.authenticated_userid(request)
        self.assertIsNone(result)

    def test_authenticated_userid_returns_user_id(self):
        """AuthTokenAuthenticationPolicy.authenticated_userid() returns an authenticated ObjectId
        """
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        expected = str(self.user.id)
        request.user = self.user
        result = self.auth_pol.authenticated_userid(request)
        self.assertEqual(expected, result)

    def test_effective_principals_includes_authenticated_user_id(self):
        """AuthTokenAuthenticationPolicy.effective_principals() includes an authenticated ObjectId
        """
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        request.user = self.user
        expected = str(self.user.id)
        result = self.auth_pol.effective_principals(request)
        self.assertIn(expected, result)

    def test_effective_principals_includes_everyone_for_unauthenticated_user(self):
        """AuthTokenAuthenticationPolicy.effective_principals() includes Everyone for an authenticated user
        """
        from pyramid.testing import DummyRequest
        from pyramid.authentication import Everyone
        request = DummyRequest()
        request.user = None
        result = self.auth_pol.effective_principals(request)
        self.assertIn(Everyone, result)

    def test_effective_principals_exclude_authenticated_for_unauthenticated_user(self):
        """AuthTokenAuthenticationPolicy.effective_principals() excludes "Authenticated" for an authenticated user
        """
        from pyramid.testing import DummyRequest
        from pyramid.authentication import Authenticated
        request = DummyRequest()
        request.user = None
        result = self.auth_pol.effective_principals(request)
        self.assertNotIn(Authenticated, result)

    def test_effective_principals_include_authenticated_for_authenticated_user(self):
        """AuthTokenAuthenticationPolicy.effective_principals() excludes "Authenticated" for an authenticated user
        """
        from pyramid.testing import DummyRequest
        from pyramid.authentication import Authenticated
        request = DummyRequest()
        request.user = self.user
        result = self.auth_pol.effective_principals(request)
        self.assertIn(Authenticated, result)

    def test_effective_principals_include_assigned_groups_for_authenticated_user(self):
        """AuthTokenAuthenticationPolicy.effective_principals() includes assigned groups for an authenticated user
        """
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        request.user = self.user
        result = self.auth_pol.effective_principals(request)
        for expected in self.user.groups:
            self.assertIn(expected, result)
