import unittest

from stackcite.users import testing


class CreateRequestTestCase(unittest.TestCase):

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
