import unittest

from stackcite.api import testing


class CreateConfirmationTokenTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from .. import conf
        self.schema = conf.CreateConfirmationToken()

    def test_user_id_required(self):
        """CreateConfirmationToken.email is required
        """
        result = self.schema.load({}).errors.keys()
        self.assertIn('email', result)


class UpdateConfirmationTokenTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from .. import conf
        self.schema = conf.UpdateConfirmationToken()

    def test_user_id_required(self):
        """ConfirmConfirmationToken.key is required
        """
        result = self.schema.load({}).errors.keys()
        self.assertIn('key', result)
