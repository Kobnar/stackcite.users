from pyramid.view import view_defaults, view_config

from stackcite.api import views, exceptions as api_exc
from stackcite.users import resources, schema, exceptions as exc


@view_defaults(context=resources.UserDocument, renderer='json')
class UserDocumentViews(views.APIDocumentViews):

    @view_config(request_method='PUT', permission='update')
    @views.managed_view
    def update(self):
        try:
            return super().update()
        except exc.AuthenticationError:
            raise api_exc.APIAuthenticationFailed()


@view_defaults(context=resources.UserCollection, renderer='json')
class UserCollectionViews(views.APICollectionViews):

    @view_config(request_method='POST', permission='create')
    @views.managed_view
    def create(self):
        data = self.request.json_body
        schm = schema.User(strict=True, only=('id', 'email', 'password'))
        data = schm.load(data).data
        user = self.context.create(data)
        result, errors = schm.dump(user)
        self.request.response.status = 201
        return result
