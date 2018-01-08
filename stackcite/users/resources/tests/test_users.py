import unittest

from stackcite.users import testing


class UserResourceTests(unittest.TestCase):

    def setUp(self):
        from stackcite.users import resources
        self.col_rec = resources.UserCollection(None, 'users')


class UserCollectionTests(UserResourceTests):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        super().setUp()

        from stackcite.users import models
        models.User.drop_collection()
        models.ConfirmToken.drop_collection()
        models.AuthToken.drop_collection()

    def test_create_user_creates_user(self):
        """UserCollection.create() creates a User
        """
        email = 'test@email.com'
        data = {
            'email': email,
            'password': 'T3stPa$$word'}
        self.col_rec.create(data)
        from stackcite.users import models
        import mongoengine
        try:
            models.User.objects.get(email=email)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg=msg.format(err))

    def test_create_user_creates_confirm_token(self):
        """UserCollection.create() creates a ConfirmToken
        """
        email = 'test@email.com'
        data = {
            'email': email,
            'password': 'T3stPa$$word'}
        user = self.col_rec.create(data)
        from stackcite.users import models
        import mongoengine
        try:
            models.ConfirmToken.objects.get(_user__id=user.id)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg=msg.format(err))


class UserDocumentTests(UserResourceTests):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        super().setUp()

        from stackcite.users import models
        models.User.drop_collection()
        models.ConfirmToken.drop_collection()
        models.AuthToken.drop_collection()

        user = testing.utils.create_user(
            'test@email.com', 'T3stPa$$word', save=True)

        self.doc_rec = self.col_rec[user.id]

    def test_update_email_changes_email(self):
        """UserDocument.update() changes an email address
        """
        data = {
            'email': 'new@email.com'}
        user = self.doc_rec.update(data)
        from stackcite.users import models
        from stackcite.users import exceptions as exc
        try:
            models.User.authenticate(user.email, 'T3stPa$$word')
        except exc.AuthenticationError as err:
            msg = 'Unexpected exception raised: {}'.format(err)
            self.fail(msg)

    def test_update_new_password_changes_existing_password(self):
        """UserDocument.update() changes an existing password
        """
        data = {
            'new_password': 'N3wPa$$word',
            'password': 'T3stPa$$word'}
        user = self.doc_rec.update(data)
        from stackcite.users import models
        from stackcite.users import exceptions as exc
        try:
            models.User.authenticate(user.email, 'N3wPa$$word')
        except exc.AuthenticationError as err:
            msg = 'Unexpected exception raised: {}'.format(err)
            self.fail(msg)

    def test_update_new_password_invalid_password_raises_exception(self):
        """UserDocument.update() raises exception if password is invalid
        """
        data = {
            'new_password': 'N3wPa$$word',
            'password': 'invalid_password'}
        from stackcite.api.models.validators import exceptions as exc
        with self.assertRaises(exc.ValidationError):
            self.doc_rec.update(data)

    def test_update_new_password_wrong_password_raises_exception(self):
        """UserDocument.update() raises exception if password is wrong
        """
        data = {
            'new_password': 'N3wPa$$word',
            'password': 'S0mePa$$word'}
        from stackcite.users import exceptions as exc
        with self.assertRaises(exc.AuthenticationError):
            self.doc_rec.update(data)

    def test_update_invalid_new_password_raises_exception(self):
        """UserDocument.update() raises exception if new_password is invalid
        """
        data = {
            'new_password': 'invalid_password',
            'password': 'T3stPa$$word'}
        from stackcite.api.models.validators import exceptions as exc
        with self.assertRaises(exc.ValidationError):
            self.doc_rec.update(data)

    def test_delete_user_deletes_auth_tokens(self):
        """UserDocument.delete() deletes associated auth tokens
        """
        from stackcite.users import models
        models.AuthToken.drop_collection()
        user = self.doc_rec.retrieve()
        token = models.AuthToken.new(user, save=True)
        self.doc_rec.delete()
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.AuthToken.objects.get(_key=token.key)

    def test_delete_user_deletes_confirm_tokens(self):
        """UserDocument.delete() deletes associated confirm tokens
        """
        from stackcite.users import models
        models.ConfirmToken.drop_collection()
        user = self.doc_rec.retrieve()
        token = models.ConfirmToken.new(user, save=True)
        self.doc_rec.delete()
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.ConfirmToken.objects.get(_key=token.key)
