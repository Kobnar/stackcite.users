import unittest

from stackcite.users import testing


class AuthenticationErrorBaseTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import AuthenticationError
        expected = 'Authentication failed'
        error = AuthenticationError()
        result = error.message
        self.assertEqual(expected, result)
