from stackcite.api import testing


class ConfirmationViewsTests(testing.views.BaseViewTestCase):

    layer = testing.layers.MongoTestLayer

    from stackcite.users import resources
    RESOURCE_CLASS = resources.ConfirmResource

    from stackcite.users.views import ConfirmationViews
    VIEW_CLASS = ConfirmationViews

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.ConfirmToken.drop_collection()
        super().setUp()


class ConfirmationViewsCreateTests(ConfirmationViewsTests):

    def test_create_creates_confirmation_token(self):
        """ConfirmationViews.create() creates ConfirmationToken in database
        """
        view = self.make_view()
        email = 'test@email.com'
        password = 'T3stPa$$word'
        from stackcite.users import models
        user = models.User.new(email, password, save=True)
        view.request.json_body = {'email': email}
        view.create()
        import mongoengine
        try:
            models.ConfirmToken.objects.get(_user=user)
        except mongoengine.DoesNotExist as err:
            msg = 'ConfirmationToken does not exist: {}'.format(err)
            self.fail(msg=msg)

    def test_strict_schema(self):
        """ConfirmationViews.create() enforces a strict validation schema
        """
        view = self.make_view()
        view.request.json_body = {'email': 'bad_email'}
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIValidationError):
            view.create()

    def test_confirmed_user_raises_403_FORBIDDEN(self):
        """ConfirmationViews.Create() returns 403 FORBIDDEN if user already confirmed
        """
        view = self.make_view()
        email = 'test@email.com'
        password = 'T3stPa$$word'
        from stackcite.users import auth, models
        user = models.User.new(email, password)
        user.add_group(auth.USERS)
        user.save()
        view.request.json_body = {'email': email}
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIForbidden):
            view.create()


class ConfirmationViewsUpdateTests(ConfirmationViewsTests):

    def setUp(self):
        super().setUp()
        from stackcite.users import models
        self.user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        self.token = models.ConfirmToken.new(self.user, save=True)

    def test_update_deletes_confirmation_token(self):
        """ConfirmationViews.update() deletes ConfirmationToken in database
        """
        view = self.make_view()
        view.request.json_body = {'key': self.token.key}
        view.update()
        import mongoengine
        from stackcite.users import models
        with self.assertRaises(mongoengine.DoesNotExist):
            models.ConfirmToken.objects.get(_key=self.token.key)

    def test_update_confirms_user(self):
        """ConfirmationViews.update() confirms associated user
        """
        view = self.make_view()
        view.request.json_body = {'key': self.token.key}
        view.update()
        self.user.reload()
        self.assertIsNotNone(self.user.confirmed)

    def test_strict_schema(self):
        """ConfirmationViews.update() enforces a strict validation schema
        """
        view = self.make_view()
        view.request.json_body = {'email': 'bad_email'}
        from stackcite.api import exceptions as exc
        with self.assertRaises(exc.APIValidationError):
            view.update()
