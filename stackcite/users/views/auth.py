import marshmallow
import mongoengine

from mongoengine import context_managers
from pyramid.view import view_defaults, view_config

from stackcite.api import views, exceptions as api_exc
from stackcite.users import models, exceptions as exc, resources, schema


@view_defaults(context=resources.AuthResource, renderer='json')
class AuthViews(views.BaseView):

    @view_config(request_method='POST', permission='create')
    def create(self):
        try:
            auth_data = self.request.json_body
            auth_schm = schema.Authenticate(strict=True)
            auth_data, errors = auth_schm.load(auth_data)
            auth_token = self.context.create(auth_data)
            with context_managers.no_dereference(models.AuthToken):
                token_schm = schema.AuthToken()
                auth_token, errors = token_schm.dump(auth_token)
            self.request.response.status_code = 201
            return auth_token

        except ValueError:
            raise api_exc.APIDecodingError()

        except marshmallow.ValidationError as err:
            errors = err.messages
            raise api_exc.APIValidationError(detail=errors)

        except (mongoengine.DoesNotExist, exc.AuthenticationError):
            raise api_exc.APIAuthenticationFailed()

    @view_config(request_method='GET', permission='retrieve')
    def retrieve(self):
        token = self.request.token
        auth_token = self.context.retrieve(token)
        schm = schema.AuthToken()
        auth_token, errors = schm.dump(auth_token)
        return auth_token

    @view_config(request_method='PUT', permission='update')
    def update(self):
        token = self.request.token
        auth_token = self.context.update(token)
        schm = schema.AuthToken()
        auth_token, errors = schm.dump(auth_token)
        return auth_token

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        token = self.request.token
        self.context.delete(token)
        raise api_exc.APINoContent()
