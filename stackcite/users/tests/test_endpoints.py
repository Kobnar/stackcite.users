from stackcite.users import testing


def _authenticate_user(email, password):
    from stackcite.users import models
    user = models.User.authenticate(email, password)
    token = testing.utils.create_auth_token(user, save=True)
    key = str(token.key)
    return key


class AuthEndpointTests(testing.endpoints.APIEndpointTestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.AuthToken.drop_collection()
        super().setUp()
        user = testing.utils.create_user(**self.auth_data, save=True)
        self.user_id = str(user.id)

    @property
    def auth_data(self):
        return {
            'email': 'test@email.com',
            'password': 'T3stPa$$word'
        }

    @staticmethod
    def authenticate_user(email, password):
        return _authenticate_user(email, password)

    def test_create_returns_201(self):
        """Successful POST returns 201 CREATED
        """
        response = self.test_app.post_json('/auth/', params=self.auth_data)
        result = response.status_code
        self.assertEqual(201, result)

    def test_create_returns_key(self):
        """Successful POST returns key field
        """
        response = self.test_app.post_json('/auth/', params=self.auth_data)
        result = response.json_body.get('key')
        self.assertIsNotNone(result)

    def test_create_invalid_json_body_returns_400(self):
        """POST with a malformed JSON body returns 400 BAD REQUEST
        """
        json_data = '{"this": is {horrible": data}'
        response = self.test_app.post(
            '/auth/', params=json_data, expect_errors=True)
        result = response.status_code
        self.assertEqual(400, result)

    def test_create_invalid_data_returns_400(self):
        """POST with invalid data returns 400 BAD REQUEST
        """
        json_data = {'email': 'invalid_email', 'password': 'invalid_password'}
        response = self.test_app.post_json(
            '/auth/', params=json_data, expect_errors=True)
        result = response.status_code
        self.assertEqual(400, result)

    def test_create_wrong_credentials_returns_400(self):
        """POST with wrong credentials returns 403 FORBIDDEN
        """
        json_data = {'email': 'test@email.com', 'password': 'Wr0ngPa$$word'}
        response = self.test_app.post_json(
            '/auth/', params=json_data, expect_errors=True)
        result = response.status_code
        self.assertEqual(403, result)

    def test_retrieve_returns_403(self):
        """GET returns 403 FORBIDDEN
        """
        response = self.test_app.get('/auth/', expect_errors=True)
        result = response.status_code
        self.assertEqual(403, result)

    def test_update_returns_403(self):
        """GET returns 403 FORBIDDEN
        """
        response = self.test_app.get('/auth/', expect_errors=True)
        result = response.status_code
        self.assertEqual(403, result)

    def test_delete_returns_403(self):
        """GET returns 403 FORBIDDEN
        """
        response = self.test_app.get('/auth/', expect_errors=True)
        result = response.status_code
        self.assertEqual(403, result)

    def test_authenticated_retrieve_returns_200(self):
        """Authenticated GET returns 200 OK
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get('/auth/', headers=headers)
        result = response.status_code
        self.assertEqual(200, result)

    def test_authenticated_retrieve_returns_key(self):
        """Authenticated GET returns key field
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get('/auth/', headers=headers)
        result = response.json_body.get('key')
        self.assertIsNotNone(result)

    def test_authenticated_update_returns_200(self):
        """Authenticated PUT returns 200 OK
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put('/auth/', headers=headers)
        result = response.status_code
        self.assertEqual(200, result)

    def test_authenticated_update_returns_key(self):
        """Authenticated PUT returns key field
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put('/auth/', headers=headers)
        result = response.json_body.get('key')
        self.assertIsNotNone(result)

    def test_authenticated_delete_returns_204(self):
        """Authenticated DELETE returns 204 NO CONTENT
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.delete('/auth/', headers=headers)
        result = response.status_code
        self.assertEqual(204, result)


class ConfEndpointTests(testing.endpoints.APIEndpointTestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.ConfirmToken.drop_collection()
        super().setUp()
        auth_data = {
            'email': 'test@email.com',
            'password': 'T3stPa$$word'}
        self.user = testing.utils.create_user(**auth_data, save=True)

    def test_create_returns_201(self):
        """Successful POST returns 201 CREATED
        """
        json_data = {'email': 'test@email.com'}
        response = self.test_app.post_json('/conf/', params=json_data)
        result = response.status_code
        self.assertEqual(201, result)

    def test_create_returns_empty_body(self):
        """Successful POST returns None
        """
        json_data = {'email': 'test@email.com'}
        response = self.test_app.post_json('/conf/', params=json_data)
        result = response.json_body
        self.assertIsNone(result)

    def test_create_confirmed_user_returns_403(self):
        """POST request for a confirmed user returns 403 FORBIDDEN
        """
        from stackcite.users import auth
        self.user.add_group(auth.USERS)
        self.user.save()
        json_data = {'email': 'test@email.com'}
        response = self.test_app.post_json('/conf/', params=json_data, expect_errors=True)
        result = response.status_code
        self.assertEqual(403, result)

    def test_update_returns_200(self):
        """Successful PUT returns 200 OK
        """
        conf_token = testing.utils.create_conf_token(self.user, save=True)
        json_data = {'key': conf_token.key}
        response = self.test_app.put_json('/conf/', params=json_data)
        result = response.status_code
        self.assertEqual(200, result)

    def test_update_returns_user_id(self):
        """Successful PUT returns 200 OK
        """
        conf_token = testing.utils.create_conf_token(self.user, save=True)
        json_data = {'key': conf_token.key}
        response = self.test_app.put_json('/conf/', params=json_data)
        expected = str(self.user.id)
        result = response.json_body['user']['id']
        self.assertEqual(expected, result)


class UsersEndpointTests(testing.endpoints.APIEndpointTestCase):

    layer = testing.layers.MongoTestLayer

    def setUp(self):
        from stackcite.users import models
        models.User.drop_collection()
        models.AuthToken.drop_collection()
        models.ConfirmToken.drop_collection()
        super().setUp()

    @property
    def auth_data(self):
        return {
            'email': 'test@email.com',
            'password': 'T3stPa$$word'
        }

    @staticmethod
    def authenticate_user(email, password):
        return _authenticate_user(email, password)


class UsersCollectionEndpointTests(UsersEndpointTests):

    def test_create_returns_201(self):
        """Successful POST returns 201 CREATED
        """
        response = self.test_app.post_json('/', params=self.auth_data)
        result = response.status_code
        self.assertEqual(201, result)

    def test_create_returns_valid_object_id(self):
        """Successful POST returns valid ObjectId
        """
        import bson
        response = self.test_app.post_json(
            '/', content_type='applicaiton/json', params=self.auth_data)
        user_id = response.json_body['id']
        result = bson.ObjectId.is_valid(user_id)
        self.assertTrue(result)

    def test_create_invalid_json_body_returns_400(self):
        """POST with a malformed JSON body returns 400 BAD REQUEST
        """
        json_data = '{"this": is {horrible": data}'
        response = self.test_app.post_json(
            '/', content_type='applicaiton/json', params=json_data,
            expect_errors=True)
        result = response.status_code
        self.assertEqual(400, result)

    def test_create_invalid_email_returns_400(self):
        """POST with invalid email returns 400 BAD REQUEST
        """
        json_data = {
            'email': 'invalid_email',
            'password': 'T3stPa$$word'}
        response = self.test_app.post_json(
            '/', params=json_data, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_create_invalid_password_returns_400(self):
        """POST with invalid password returns 400 BAD REQUEST
        """
        json_data = {
            'email': 'test@email.com',
            'password': 'InvalidPassword'}
        response = self.test_app.post_json(
            '/', params=json_data, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_unauthenticated_retrieve_users_returns_403(self):
        """Unauthenticated GET returns 403 FORBIDDEN
        """
        response = self.test_app.get('/', expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_retrieve_users_returns_403(self):
        """Authenticated GET as default group returns 403 FORBIDDEN
        """
        testing.utils.create_user(
            self.auth_data['email'],
            self.auth_data['password'],
            save=True)
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get('/', headers=headers, expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_staff_retrieve_users_returns_403(self):
        """Authenticated GET as STAFF returns 403 FORBIDDEN
        """
        from stackcite.users import auth
        testing.utils.create_user(
            self.auth_data['email'],
            self.auth_data['password'],
            groups=[auth.STAFF],
            save=True)
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get('/', headers=headers, expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_admin_retrieve_users_returns_200(self):
        """Authenticated GET as ADMIN returns 200 OK
        """
        from stackcite.users import auth
        testing.utils.create_user(
            self.auth_data['email'],
            self.auth_data['password'],
            groups=[auth.ADMIN],
            save=True)
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get('/', headers=headers)
        self.assertEqual(200, response.status_code)


class UsersDocumentEndpointTests(UsersEndpointTests):

    def setUp(self):
        super().setUp()
        user = testing.utils.create_user(**self.auth_data, save=True)
        self.user_id = str(user.id)

    def test_unauthenticated_retrieve_returns_403(self):
        """Unauthenticated GET returns 403 FORBIDDEN
        """
        response = self.test_app.get(
            '/{}/'.format(self.user_id),
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_unauthenticated_update_returns_403(self):
        """Unauthenticated PUT returns 403 FORBIDDEN
        """
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_unauthenticated_delete_returns_403(self):
        """Unauthenticated DELETE returns 403 FORBIDDEN
        """
        response = self.test_app.delete(
            '/{}/'.format(self.user_id),
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_retrieve_returns_200(self):
        """Authenticated GET returns 200 OK
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get(
            '/{}/'.format(self.user_id),
            headers=headers)
        self.assertEqual(200, response.status_code)

    def test_authenticated_update_returns_200(self):
        """Authenticated PUT to 'users/{id}/' returns 200 OK
        """
        new_data = {'email': 'changed@email.com'}
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            headers=headers,
            params=new_data)
        self.assertEqual(200, response.status_code)

    def test_authenticated_update_invalid_json_body_returns_400(self):
        """Authenticated PUT with malformed JSON body returns 400 BAD REQUEST
        """
        new_data = '{"this": {horrible": data}'
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put(
            '/{}/'.format(self.user_id),
            headers=headers,
            params=new_data,
            expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_authenticated_update_with_wrong_password_returns_403(self):
        """Authenticated PUT with wrong password returns 403
        """
        new_data = {
            'password': 'Wr0ngPa$$word',
            'new_password': 'N3wPa$$word'}
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            headers=headers,
            params=new_data,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_update_groups_returns_403(self):
        """Authenticated PUT to change own groups returns 403 FORBIDDEN
        """
        new_data = {'groups': ['users', 'staff']}
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            headers=headers,
            params=new_data,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_authenticated_delete_returns_200(self):
        """Authenticated DELETE returns 204 NO CONTENT
        """
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.delete(
            '/{}/'.format(self.user_id),
            headers=headers)
        self.assertEqual(204, response.status_code)

    def test_authenticated_retrieve_different_user_returns_403(self):
        """Authenticated GET different user returns 403 FORBIDDEN
        """
        user_2_auth_data = {
            'email': 'user2@email.com',
            'password': 'T3stPa$$word'}
        user_2 = testing.utils.create_user(
            user_2_auth_data['email'],
            user_2_auth_data['password'],
            save=True)
        user_2_id = str(user_2.id)
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.get(
            '/{}/'.format(user_2_id),
            headers=headers,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_staff_retrieve_different_user_returns_403(self):
        """GET different user as STAFF returns 403 FORBIDDEN
        """
        staff_auth_data = {
            'email': 'admin@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(
            staff_auth_data['email'],
            staff_auth_data['password'],
            groups=['staff'],
            save=True)
        staff_key = self.authenticate_user(**staff_auth_data)
        headers = {'Authorization': 'key {}'.format(staff_key)}
        response = self.test_app.get(
            '/{}/'.format(self.user_id),
            headers=headers,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_admin_retrieve_different_user_returns_200(self):
        """GET different user as ADMIN returns 200 OK
        """
        admin_auth_data = {
            'email': 'admin@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(
            admin_auth_data['email'],
            admin_auth_data['password'],
            groups=['admin'],
            save=True)
        admin_key = self.authenticate_user(**admin_auth_data)
        headers = {'Authorization': 'key {}'.format(admin_key)}
        response = self.test_app.get(
            '/{}/'.format(self.user_id),
            headers=headers)
        self.assertEqual(200, response.status_code)

    def test_authenticated_update_different_user_returns_403(self):
        """PUT to different user returns 403 FORBIDDEN
        """
        user_2_auth_data = {
            'email': 'user2@email.com',
            'password': 'T3stPa$$word'}
        user_2 = testing.utils.create_user(
            user_2_auth_data['email'],
            user_2_auth_data['password'],
            save=True)
        new_data = {'groups': ['users', 'staff']}
        user_2_id = str(user_2.id)
        key = self.authenticate_user(**self.auth_data)
        headers = {'Authorization': 'key {}'.format(key)}
        response = self.test_app.put(
            '/{}/'.format(user_2_id),
            headers=headers,
            expect_errors=True,
            params=new_data)
        self.assertEqual(403, response.status_code)

    def test_staff_update_different_user_returns_403(self):
        """PUT to different user as STAFF returns 403 FORBIDDEN
        """
        staff_auth_data = {
            'email': 'admin@email.com',
            'password': 'T3stPa$$word'}
        new_user_data = {
            'email': 'other@email.com'}
        testing.utils.create_user(
            staff_auth_data['email'],
            staff_auth_data['password'],
            groups=['staff'],
            save=True)
        staff_key = self.authenticate_user(**staff_auth_data)
        headers = {'Authorization': 'key {}'.format(staff_key)}
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            headers=headers,
            params=new_user_data,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_admin_update_different_user_returns_200(self):
        """PUT to different user as ADMIN returns 200 OK
        """
        admin_auth_data = {
            'email': 'admin@email.com',
            'password': 'T3stPa$$word'}
        new_user_data = {
            'email': 'other@email.com'}
        testing.utils.create_user(
            admin_auth_data['email'],
            admin_auth_data['password'],
            groups=['admin'],
            save=True)
        admin_key = self.authenticate_user(**admin_auth_data)
        headers = {'Authorization': 'key {}'.format(admin_key)}
        response = self.test_app.put_json(
            '/{}/'.format(self.user_id),
            content_type='application/json',
            headers=headers,
            params=new_user_data)
        self.assertEqual(200, response.status_code)

    def test_authenticated_delete_different_user_returns_403(self):
        """Authenticated DELETE different user returns 403 FORBIDDEN
        """
        user_2_auth_data = {
            'email': 'user2@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(
            user_2_auth_data['email'],
            user_2_auth_data['password'],
            save=True)
        admin_key = self.authenticate_user(**user_2_auth_data)
        headers = {'Authorization': 'key {}'.format(admin_key)}
        response = self.test_app.delete(
            '/{}/'.format(self.user_id),
            headers=headers,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_staff_delete_different_user_returns_403(self):
        """DELETE different user as STAFF returns 403 FORBIDDEN
        """
        staff_auth_data = {
            'email': 'staff@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(
            staff_auth_data['email'],
            staff_auth_data['password'],
            groups=['staff'],
            save=True)
        admin_key = self.authenticate_user(**staff_auth_data)
        headers = {'Authorization': 'key {}'.format(admin_key)}
        response = self.test_app.delete(
            '/{}/'.format(self.user_id),
            headers=headers,
            expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_admin_delete_different_user_returns_204(self):
        """DELETE different user as ADMIN returns 204 OK
        """
        admin_auth_data = {
            'email': 'admin@email.com',
            'password': 'T3stPa$$word'}
        testing.utils.create_user(
            admin_auth_data['email'],
            admin_auth_data['password'],
            groups=['admin'],
            save=True)
        admin_key = self.authenticate_user(**admin_auth_data)
        headers = {'Authorization': 'key {}'.format(admin_key)}
        response = self.test_app.delete(
            '/{}/'.format(self.user_id),
            headers=headers)
        self.assertEqual(204, response.status_code)
