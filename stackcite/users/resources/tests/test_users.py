import unittest

from stackcite.users import testing


class UserResourceTestCase(unittest.TestCase):

    def setUp(self):
        from stackcite.users import resources
        self.col_rec = resources.UserCollection(None, 'users')


class UserDocumentTestCase(UserResourceTestCase):

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
