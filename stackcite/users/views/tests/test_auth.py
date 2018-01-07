from stackcite.users import testing


class AuthViewsTests(testing.views.CollectionViewTestCase):

    layer = testing.layers.MongoTestLayer

    from stackcite.users import resources
    from stackcite.users import views
    RESOURCE_CLASS = resources.AuthResource
    VIEW_CLASS = views.AuthViews

    def setUp(self):
        from stackcite.users import models
        models.AuthToken.drop_collection()
        models.User.drop_collection()
        super().setUp()

    def make_view(self, name='api_v1'):
        return super().make_view(name)

    def test_create_success_returns_201(self):
        """AuthViews.create() success returns 201 CREATED
        """
        data = {
            'email': 'test@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(data['email'], data['password'], save=True)
        view = self.make_view()
        view.request.json_body = data
        view.create()
        result = view.request.response.status_code
        self.assertEqual(201, result)

    def test_create_invalid_data_returns_400(self):
        """AuthViews.create() with invalid models raises 400 BAD REQUEST
        """
        from stackcite.api import exceptions as exc
        data = {
            'cats': 'Are evil.',
            'dogs': 'Are lovely.'}
        testing.utils.create_user('test@email.com', 'T3stPa$$word', save=True)
        view = self.make_view()
        view.request.json_body = data
        with(self.assertRaises(exc.APIValidationError)):
            view.create()

    def test_create_no_user_returns_400(self):
        """AuthViews.create() with unregistered user raises 403 UNAUTHORIZED
        """
        from stackcite.api import exceptions as exc
        data = {
            'email': 'wrong@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user('test@email.com', data['password'], save=True)
        view = self.make_view()
        view.request.json_body = data
        with(self.assertRaises(exc.APIAuthenticationFailed)):
            view.create()

    def test_create_wrong_password_returns_400(self):
        """AuthViews.create() with wrong password raises 403 UNAUTHORIZED
        """
        from stackcite.api import exceptions as exc
        data = {
            'email': 'test@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(data['email'], 'B4dPa$$word', save=True)
        view = self.make_view()
        view.request.json_body = data
        with(self.assertRaises(exc.APIAuthenticationFailed)):
            view.create()

    def test_retrieve_returns_token_key(self):
        """AuthViews.retrieve() returns an auth token with key
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        token = testing.utils.create_auth_token(user, save=True)
        expected = str(token.id)
        view = self.make_view()
        view.request.token = token
        result = view.retrieve()['key']
        self.assertEqual(expected, result)

    def test_retrieve_returns_user_with_id(self):
        """AuthViews.retrieve() returns a user with an ObjectId
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        token = testing.utils.create_auth_token(user, save=True)
        expected = str(user.id)
        view = self.make_view()
        view.request.token = token
        result = view.retrieve()['user']['id']
        self.assertEqual(expected, result)

    def test_retrieve_returns_user_with_groups(self):
        """AuthViews.retrieve() returns a user with a list of groups
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        user.add_group('users')
        token = testing.utils.create_auth_token(user, save=True)
        expected = ['users']
        view = self.make_view()
        view.request.token = token
        result = view.retrieve()['user']['groups']
        self.assertEqual(expected, result)

    def test_update_returns_token_key(self):
        """AuthViews.update() returns an auth token with key
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        token = testing.utils.create_auth_token(user, save=True)
        expected = str(token.id)
        view = self.make_view()
        view.request.token = token
        result = view.update()['key']
        self.assertEqual(expected, result)

    def test_delete_raises_exception(self):
        """AuthViews.delete() raises exception
        """
        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)
        token = testing.utils.create_auth_token(user, save=True)
        view = self.make_view()
        view.request.token = token
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APINoContent):
            view.delete()
