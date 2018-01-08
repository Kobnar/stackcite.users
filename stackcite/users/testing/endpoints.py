import unittest

from . import layers


class APIEndpointTests(unittest.TestCase):

    layer = layers.WSGITestLayer

    def setUp(self):
        self.test_app = self.make_app()

    @staticmethod
    def make_app():
        """
        Instantiates a WSGI application object.
        """
        from pyramid import paster
        import stackcite.users
        import webtest
        settings = paster.get_appsettings('development.ini')
        app = stackcite.users.main(global_config=None, **settings)
        return webtest.TestApp(app)
