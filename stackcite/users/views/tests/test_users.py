from stackcite.users import testing


class UserCollectionCreateViewTests(testing.views.CollectionViewTestCase):

    layer = testing.layers.MongoTestLayer

    from stackcite.users import resources
    from stackcite.users import views
    RESOURCE_CLASS = resources.UserCollection
    VIEW_CLASS = views.UserCollectionViews

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()

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


class UserDocumentViewTests(testing.views.DocumentViewTestCase):

    layer = testing.layers.MongoTestLayer

    from stackcite.users import resources
    from stackcite.users import views
    RESOURCE_CLASS = resources.UserCollection
    VIEW_CLASS = views.UserDocumentViews

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()

    def make_view(self, object_id=None, name='documents'):
        return super().make_view(object_id, name)

    def test_update_wrong_password_raises_exception(self):
        """UserDocumentViews.update() raises exception for wrong password
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        view = self.make_view(user.id)
        params = {
            'password': 'Wr0ngPa$$word',
            'new_password': '0therPa$$word'}
        view.request.json_body = params
        view.request.user = None
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIAuthenticationFailed):
            view.update()
