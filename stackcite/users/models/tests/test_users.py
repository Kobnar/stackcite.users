import unittest

import mongoengine

from stackcite.users import testing


class UserBaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import users
        self.user = users.User()


class UserUnitTestCase(UserBaseTestCase):

    layer = testing.layers.UnitTestLayer

    def test_email_is_required(self):
        """User.email is a required field
        """
        try:
            self.user.validate()
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('email', invalid_fields)

    def test_joined_is_required(self):
        """User.joined is a required field
        """
        try:
            self.user.validate(clean=False)
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('_joined', invalid_fields)

    def test_set_password_call_is_required(self):
        """User.set_password() call is required to validate document
        """
        try:
            self.user.validate()
        except mongoengine.ValidationError as err:
            err_dict = err.to_dict()
            invalid_fields = err_dict.keys()
            self.assertIn('_salt', invalid_fields)
            self.assertIn('_hash', invalid_fields)

    def test_group_default_is_empty_list(self):
        """User.groups defaults to an empty list
        """
        self.assertEqual(self.user.groups, [])

    def test_groups_is_read_only(self):
        """User.groups is read-only
        """
        with self.assertRaises(AttributeError):
            self.user.groups = ['users', 'admins']

    def test_add_group_adds_valid_group(self):
        """User.add_group() adds a valid group
        """
        from stackcite.users import auth
        try:
            self.user.add_group(auth.STAFF)
        except ValueError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_add_group_does_not_add_duplicate_group(self):
        """User.add_group() will not add a duplicate group
        """
        from stackcite.users import auth
        self.user.add_group(auth.USERS)
        expected = [auth.USERS]
        result = self.user.groups
        self.assertEqual(expected, result)

    def test_remove_group_removes_valid_group(self):
        """User.remove_group() removes a valid group
        """
        from stackcite.users import auth
        self.user.add_group('staff')
        try:
            self.user.remove_group(auth.STAFF)
        except ValueError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_add_group_raises_exception_for_invalid_group(self):
        """User.add_group() raises exception for invalid group
        """
        from stackcite.api.data import validators
        with self.assertRaises(validators.ValidationError):
            self.user.add_group('invalid')

    def test_remove_group_raises_exception_if_not_in_group(self):
        """User.remove_group() raises exception if not in group
        """
        with self.assertRaises(ValueError):
            self.user.remove_group('invalid')

    def test_joined_is_read_only(self):
        """User.joined is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.joined = datetime.now()

    def test_confirmed_is_read_only(self):
        """User.confirmed is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.confirmed = datetime.now()

    def test_confirm_sets_confirmed(self):
        """User.confirm() sets User.confirmed field
        """
        self.user.confirm()
        result = self.user.confirmed
        self.assertIsNotNone(result)

    def test_confirm_adds_default_group(self):
        """User.confirm() adds user to default group
        """
        self.user.confirm()
        from stackcite.users import models
        default_groups = models.User.DEFAULT_GROUPS
        for g in default_groups:
            self.assertIn(g, self.user.groups)

    def test_last_login_is_read_only(self):
        """User.last_login is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.last_login = datetime.now()

    def test_prev_login_is_read_only(self):
        """User.prev_login is read-only
        """
        from datetime import datetime
        with self.assertRaises(AttributeError):
            self.user.previous_login = datetime.now()

    def test_touch_login_sets_last_login(self):
        """User.touch_login() sets 'last_login'
        """
        self.user.touch_login()
        self.assertIsNotNone(self.user.last_login)

    def test_second_touch_login_sets_new_last_login(self):
        """User.touch_login() sets new 'last_login' if called twice
        """
        self.user.touch_login()
        first_login = self.user.last_login
        import time
        time.sleep(0.01)
        self.user.touch_login()
        self.assertNotEqual(first_login, self.user.last_login)

    def test_first_touch_login_does_not_set_previous_login(self):
        """User.touch_login() does not change 'previous_login' if called once
        """
        self.user.touch_login()
        self.assertIsNone(self.user.previous_login)

    def test_second_touch_login_sets_previous_login(self):
        """User.touch_login() changes 'previous_login' if called twice
        """
        self.user.touch_login()
        self.user.touch_login()
        self.assertIsNotNone(self.user.previous_login)

    def test_touch_login_sets_previous_login_to_last_login(self):
        """User.touch_login() sets 'previous_login' to original 'last_login'
        """
        from itertools import repeat
        for _ in repeat(None, 3):
            self.user.touch_login()
            first_login = self.user.last_login
            import time
            time.sleep(0.01)
            self.user.touch_login()
            self.assertEqual(first_login, self.user.previous_login)

    def test_set_password_passes_validation_with_valid_passwords(self):
        """User.set_password() accepts valid passwords
        """
        test_data = testing.data.validation.valid_passwords()
        for valid_password in test_data:
            try:
                self.user.set_password(valid_password)
            except mongoengine.ValidationError as err:
                msg = 'Unexpected exception raised: {}'
                self.fail(msg.format(err))

    def test_set_password_fails_validation_with_invalid_passwords(self):
        """User.set_password() raises exception for invalid passwords
        """
        test_data = testing.data.validation.invalid_passwords()
        from stackcite.api.data import validators
        for invalid_password in test_data:
            with self.assertRaises(validators.ValidationError):
                self.user.set_password(invalid_password)

    def test_check_password_returns_false_if_password_not_set(self):
        """User.check_password() returns false if password has not been set
        """
        result = self.user.check_password('T3stPa$$word')
        self.assertFalse(result)

    def test_check_password_fails_validation_with_invalid_passwords(self):
        """User.check_password() raises exception for invalid passwords
        """
        self.user.set_password('T3stPa$$word')
        test_data = testing.data.validation.invalid_passwords()
        from stackcite.api.data import validators
        for invalid_password in test_data:
            with self.assertRaises(validators.ValidationError):
                self.user.check_password(invalid_password)

    def test_check_password_matches_correct_passwords(self):
        """User.check_password() returns True for correct passwords
        """
        test_data = testing.data.validation.valid_passwords()
        for password in test_data:
            self.user.set_password(password)
            result = self.user.check_password(password)
            self.assertTrue(result)

    def test_check_password_fails_incorrect_passwords(self):
        """User.check_password() returns False for incorrect passwords
        """
        test_data = testing.data.validation.valid_passwords()
        for password in test_data:
            self.user.set_password(password)
            result = self.user.check_password('Wr0ngPa$$word')
            self.assertFalse(result)

    def test_password_passes_validation_with_valid_passwords(self):
        """User.password setter accepts valid passwords
        """
        try:
            self.user.password = 'T3stPa$$word'
        except mongoengine.ValidationError as err:
            msg = 'Unexpected exception raised: {}'
            self.fail(msg.format(err))

    def test_password_fails_validation_with_invalid_passwords(self):
        """User.password setter raises exception for invalid passwords
        """
        from stackcite.api.data import validators
        with self.assertRaises(validators.ValidationError):
            self.user.password = 'invalid_password'

    def test_password_returns_false_if_no_password_set(self):
        """User.password getter returns False if no password has been set
        """
        self.assertFalse(self.user.password)

    def test_password_returns_true_if_password_set(self):
        """User.password getter returns True if password has been set
        """
        self.user.password = 'T3stPa$$word'
        self.assertTrue(self.user.password)

    def test_clean_sets_joined(self):
        """User.clean() sets 'joined' field
        """
        self.user.clean()
        self.assertIsNotNone(self.user.joined)

    def test_clean_does_not_change_joined_on_addl_saves(self):
        """User.clean() does not change 'joined' if called more than once
        """
        self.user.clean()
        first_dtg = self.user.joined
        import time
        time.sleep(0.01)
        self.user.clean()
        second_dtg = self.user.joined
        self.assertEqual(first_dtg, second_dtg)


class UserIntegrationTestCase(UserBaseTestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from .. import users
        users.User.drop_collection()
        super().setUp()

    def test_email_is_unique(self):
        """User.email
        """
        from .. import users
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        dup_user = users.User()
        dup_user.email = 'test@email.com'
        dup_user.set_password('T3stPa$$word')
        with self.assertRaises(mongoengine.NotUniqueError):
            dup_user.save()

    def test_new_does_not_save_if_save_not_set(self):
        """User.new() does not save new user by default
        """
        from .. import users
        user = users.User.new('test@email.com', 'T3stPa$$word')
        self.assertIsNone(user.id)

    def test_new_saves_user_if_save_set(self):
        """User.new() saves models if 'save=True'
        """
        from .. import users
        user = users.User.new('test@email.com', 'T3stPa$$word', True)
        self.assertIsNotNone(user.id)

    def test_authenticate_correct_password_returns_user(self):
        """User.authenticate() returns user for correct password
        """
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        from .. import users
        result = users.User.authenticate(self.user.email, 'T3stPa$$word')
        self.assertEqual(self.user, result)

    def test_authenticate_incorrect_password_raises_exception(self):
        """User.authenticate() raises exception for incorrect password
        """
        self.user.email = 'test@email.com'
        self.user.set_password('T3stPa$$word')
        self.user.save()
        from .. import users
        from stackcite.users.exceptions import AuthenticationError
        with self.assertRaises(AuthenticationError):
            users.User.authenticate(self.user.email, 'Wr0ngPa$$word')
