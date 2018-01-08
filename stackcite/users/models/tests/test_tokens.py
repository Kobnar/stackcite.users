import unittest

from stackcite.users import testing


class TokenKeyFieldTests(unittest.TestCase):

    layer = testing.layers.UnitTestLayer

    def setUp(self):
        from .. import tokens
        self.field = tokens.TokenKeyField()

    def test_validate_accepts_valid_token_key(self):
        """TokenKeyField.validate() accepts a valid token key
        """
        valid_keys = testing.data.validation.valid_keys()
        from mongoengine import ValidationError
        for key in valid_keys:
            try:
                self.field.validate(key)
            except ValidationError as err:
                self.fail(err)

    def test_validate_raises_exception_for_invalid_token_keys(self):
        """TokenKeyField.validate() raises exception for invalid token key
        """
        invalid_keys = testing.data.validation.invalid_keys()
        from mongoengine import ValidationError
        for key in invalid_keys:
            with self.assertRaises(ValidationError):
                self.field.validate(key)


class AuthTokenTests(unittest.TestCase):

    def setUp(self):
        self.user = testing.utils.create_user('test@email.com')
        self.api_token = testing.utils.create_auth_token(self.user)


class AuthTokenUnitTests(AuthTokenTests):

    layer = testing.layers.UnitTestLayer

    def test_key_is_readonly(self):
        """AuthToken.key field is read-only
        """
        with self.assertRaises(AttributeError):
            self.api_token.key = '7bd8a259670a9577dc473bf4c9ef91db787aa34cad8f0ce62b93a4fe'

    def test_user_is_readonly(self):
        """AuthToken.user field is read-only
        """
        with self.assertRaises(AttributeError):
            self.api_token.user = testing.utils.create_user('test@email.com')

    def test_issued_is_readonly(self):
        """AuthToken.issued field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.api_token.issued = datetime.utcnow()

    def test_touched_is_readonly(self):
        """AuthToken.touched field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.api_token.touched = datetime.utcnow()

    def test_key_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.key field
        """
        self.assertIsNone(self.api_token.key)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.key)

    def test_issued_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.issued field
        """
        self.assertIsNone(self.api_token.issued)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.issued)

    def test_issued_static_on_clean(self):
        """AuthToken.clean() does not change AuthToken.issued field
        """
        self.api_token.clean()
        expected = self.api_token.issued
        for _ in range(5):
            self.api_token.clean()
            result = self.api_token.issued
            self.assertEqual(expected, result)

    def test_touched_set_on_clean(self):
        """AuthToken.clean() sets AuthToken.touched field
        """
        self.assertIsNone(self.api_token.touched)
        self.api_token.clean()
        self.assertIsNotNone(self.api_token.touched)

    def test_touched_updates_on_clean(self):
        """AuthToken.clean() updates AuthToken.touched field with a different value
        """
        from time import sleep
        self.api_token.clean()
        expected = self.api_token.touched
        for _ in range(5):
            sleep(0.5)
            self.api_token.clean()
            result = self.api_token.touched
            self.assertNotEqual(expected, result)

    def test_touch_updates_touched(self):
        """AuthToken.touch() sets AuthToken.touched field
        """
        self.assertIsNone(self.api_token.touched)
        self.api_token.touch()
        self.assertIsNotNone(self.api_token.touched)

    def test_invalid_key_raises_exception(self):
        """AuthToken() raises exception for invalid key string
        """
        from datetime import datetime
        from .. import tokens
        from mongoengine import ValidationError
        user = self.api_token.user
        invalid_token = tokens.AuthToken(
            _user=user,
            _key='A bad token',
            _issued=datetime.utcnow())
        with self.assertRaises(ValidationError):
            invalid_token.validate()


class AuthTokenIntegrationTests(AuthTokenTests):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from .. import users
        from .. import tokens
        users.User.drop_collection()
        tokens.AuthToken.drop_collection()
        super().setUp()
        self.user.password = 'T3stPa$$word'

    def test_user_is_not_unique(self):
        """AuthToken.user is not a unique field
        """
        self.user.save()
        from .. import tokens
        tokens.AuthToken.new(self.user, save=True)
        import mongoengine
        try:
            tokens.AuthToken.new(self.user, save=True)
        except mongoengine.NotUniqueError as err:
            self.fail(err)

    def test_new_saves_token_to_db_if_specified(self):
        """AuthToken.new() saves new token to database if 'save=True' is set
        """
        self.user.save()
        from .. import tokens
        key = tokens.AuthToken.new(self.user, save=True).key
        import mongoengine
        try:
            tokens.AuthToken.objects.get(_key=key)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))


class ConfirmTokenTests(unittest.TestCase):

    def setUp(self):
        self.user = testing.utils.create_user('test@email.com', 'T3stPa$$word')
        self.conf_token = testing.utils.create_conf_token(self.user)


class ConfirmTokenUnitTests(ConfirmTokenTests):

    layer = testing.layers.UnitTestLayer

    def test_key_is_readonly(self):
        """ConfirmToken.key field is read-only
        """
        with self.assertRaises(AttributeError):
            self.conf_token.key = '7bd8a259670a9577dc473bf4c9ef91db787aa34cad8f0ce62b93a4fe'

    def test_user_is_readonly(self):
        """ConfirmToken.user field is read-only
        """
        with self.assertRaises(AttributeError):
            self.conf_token.user = testing.utils.create_user(
                'test@email.com', 'T3stPa$$word')

    def test_issued_is_readonly(self):
        """ConfirmToken.issued field is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.conf_token.issued = datetime.utcnow()

    def test_key_set_on_clean(self):
        """ConfirmToken.clean() sets ConfirmToken.key field
        """
        self.assertIsNone(self.conf_token.key)
        self.conf_token.clean()
        self.assertIsNotNone(self.conf_token.key)

    def test_issued_set_on_clean(self):
        """ConfirmToken.clean() sets ConfirmToken.issued field
        """
        self.assertIsNone(self.conf_token.issued)
        self.conf_token.clean()
        self.assertIsNotNone(self.conf_token.issued)

    def test_issued_static_on_clean(self):
        """ConfirmToken.clean() does not change ConfirmToken.issued field
        """
        self.conf_token.clean()
        expected = self.conf_token.issued
        for _ in range(5):
            self.conf_token.clean()
            result = self.conf_token.issued
            self.assertEqual(expected, result)

    def test_invalid_key_raises_exception(self):
        """ConfirmToken() raises exception for invalid key string
        """
        from datetime import datetime
        from ..tokens import ConfirmToken
        from mongoengine import ValidationError
        user = self.conf_token.user
        invalid_token = ConfirmToken(
            _user=user,
            _key='A bad token',
            _issued=datetime.utcnow())
        with self.assertRaises(ValidationError):
            invalid_token.validate()


class ConfirmTokenIntegrationTests(ConfirmTokenTests):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from .. import users
        from .. import tokens
        users.User.drop_collection()
        tokens.ConfirmToken.drop_collection()
        super().setUp()
        self.user.password = 'T3stPa$$word'

    def test_new_saves_token_to_db_if_specified(self):
        """ConfirmToken.new() saves new token to database if 'save=True' is set
        """
        self.user.save()
        from .. import tokens
        key = tokens.ConfirmToken.new(self.user, save=True).key
        import mongoengine
        try:
            tokens.ConfirmToken.objects.get(_key=key)
        except mongoengine.DoesNotExist as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_confirm_sets_user_confirm_field_true(self):
        """ConfirmToken.confirm() sets associated User.confirmed field to 'True'
        """
        self.conf_token.confirm_user()
        result = self.user.confirmed
        self.assertTrue(result)

    def test_confirm_saves_user_confirm_to_database(self):
        """ConfirmToken.confirm() saves user confirmation to database
        """
        self.user.save()
        self.conf_token.confirm_user()
        from stackcite.users import models
        result = models.User.objects.get(id=self.user.id).confirmed
        self.assertTrue(result)

    def test_confirm_deletes_confirmation_token(self):
        """ConfirmToken.confirm() deletes confirmation token if successful
        """
        self.user.save()
        self.conf_token.save()
        key = self.conf_token.key
        self.conf_token.confirm_user()
        import mongoengine
        from stackcite.users import models
        with self.assertRaises(mongoengine.DoesNotExist):
            models.ConfirmToken.objects.get(_key=key)

    def test_confirm_returns_user(self):
        """ConfirmToken.confirm() returns associated User object
        """
        self.user.save()
        self.conf_token.save()
        expected = self.user.id
        result = self.conf_token.confirm_user().id
        self.assertEqual(expected, result)
