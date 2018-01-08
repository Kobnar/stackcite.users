import unittest

from stackcite.api import testing


class ConfirmResourceTests(unittest.TestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.ConfirmToken.drop_collection()
        from stackcite.users import resources
        self.collection = resources.ConfirmResource(None, 'confirmation')


class ConfirmResourceCreateTests(ConfirmResourceTests):

    def test_unknown_user_raises_exception(self):
        """ConfirmResource.create() raises exception for an unknown user
        """
        data = {'email': 'test@email.com'}
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            self.collection.create(data)

    def test_new_token_created_in_db(self):
        """ConfirmResource.create() creates a new confirmation token
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        data = {'email': user.email}
        self.collection.create(data)
        import mongoengine
        try:
            models.ConfirmToken.objects.get(_user=user)
        except mongoengine.DoesNotExist as err:
            self.fail(err)

    def test_existing_token_replaced_in_db(self):
        """ConfirmResource.create() creates a new confirmation token if one exists
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        prev_key = models.ConfirmToken.new(user, save=True).key
        data = {'email': user.email}
        new_key = self.collection.create(data).key
        expected = [prev_key, new_key]
        results = [t.key for t in models.ConfirmToken.objects(_user=user)]
        self.assertEqual(expected, results)

    def test_returns_confirm_token(self):
        """ConfirmResource.create() returns a ConfirmToken
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        data = {'email': user.email}
        result = self.collection.create(data)
        self.assertIsInstance(result, models.ConfirmToken)


class ConfirmResourceUpdateTests(ConfirmResourceTests):

    def test_unknown_key_raises_exception(self):
        """ConfirmResource.update() raises exception for unknown key
        """
        from stackcite.users import auth
        unknown_key = auth.utils.gen_key()
        data = {'key': unknown_key}
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            self.collection.update(data)

    def test_sets_user_confirmed_in_db(self):
        """ConfirmResource.update() confirms a known user account
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        key = models.ConfirmToken.new(user, save=True).key
        data = {'key': key}
        self.collection.update(data)
        result = models.User.objects.get(id=user.id).confirmed
        self.assertIsNotNone(result)

    def test_deletes_token(self):
        """ConfirmResource.update() deletes existing token if successful
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        key = models.ConfirmToken.new(user, save=True).key
        data = {'key': key}
        self.collection.update(data)
        import mongoengine
        with self.assertRaises(mongoengine.DoesNotExist):
            models.ConfirmToken.objects.get(_key=key)

    def test_returns_confirm_token(self):
        """ConfirmResource.update() returns 'True' if successful
        """
        from stackcite.users import models
        user = models.User.new('test@email.com', 'T3stPa$$word', save=True)
        key = models.ConfirmToken.new(user, save=True).key
        data = {'key': key}
        result = self.collection.update(data)
        self.assertTrue(result)

