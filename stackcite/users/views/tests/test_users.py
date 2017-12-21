from stackcite.api import testing


class UserCollectionViewsTests(testing.views.APIViewTestCase):

    layer = testing.layers.MongoTestLayer

    from stackcite.users import resources
    from stackcite.users import views
    RESOURCE_CLASS = resources.UserCollection
    VIEW_CLASS = views.UserCollectionViews

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()


class UserCollectionCreateViewsTests(UserCollectionViewsTests):

    def test_email_required(self):
        """UserCollectionViews.create() requires an email
        """
        view = self.make_view()
        params = {'password': 'T3stPa$$wrod'}
        view.request.json_body = params
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIBadRequest):
            view.create()

    def test_password_required(self):
        """UserCollectionViews.create() requires a password
        """
        view = self.make_view()
        params = {'email': 'test@email.com'}
        view.request.json_body = params
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIBadRequest):
            view.create()

    def test_response_includes_id(self):
        """UserCollectionViews.create() returns an ID value
        """
        view = self.make_view()
        params = {
            'email': 'test@email.com',
            'password': 'T3stPa$$wrod'}
        view.request.json_body = params
        response = view.create()
        self.assertIn('id', response)
        self.assertIsNotNone(response['id'])

    def test_user_created_in_db(self):
        """UserCollectionViews.create() creates a user
        """
        view = self.make_view()
        params = {
            'email': 'test@email.com',
            'password': 'T3stPa$$wrod'}
        view.request.json_body = params
        response = view.create()
        user_id = response['id']
        from stackcite.users import models
        from mongoengine import DoesNotExist
        try:
            models.User.objects.get(id=user_id)
        except DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))
