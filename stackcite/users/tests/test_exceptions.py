import unittest

from stackcite import testing


class AuthenticationErrorBaseTestCase(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def test_default_message(self):
        from ..exceptions import AuthenticationError
        expected = 'Authentication failed'
        error = AuthenticationError()
        result = error.message
        self.assertEqual(expected, result)
