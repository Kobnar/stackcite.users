from pyramid.view import view_defaults, view_config

from stackcite.api import views as api_views, exceptions as api_exc
from stackcite.users import resources

from . import utils


@view_defaults(context=resources.UserDocument, renderer='json')
class UserDocumentViews(api_views.APIDocumentViews):

    @view_config(request_method='PUT', permission='update')
    @utils.managed_view
    def update(self):
        data = self.request.json_body
        schm = self.context.schema(strict=True)
        data = schm.load(data).data

        # Forbid changing own group
        auth_id = str(self.request.user.id) if self.request.user else ''
        if auth_id == self.context.id and data.get('groups'):
            msg = 'A user cannot modify their own group.'
            raise api_exc.APIForbidden(detail=msg)

        result = self.context.update(data)
        result = schm.dump(result).data
        return result


@view_defaults(context=resources.UserCollection, renderer='json')
class UserCollectionViews(api_views.APICollectionViews):

    @view_config(request_method='POST', permission='create')
    @utils.managed_view
    def create(self):
        data = self.request.json_body
        schm = self.context.schema(strict=True)
        data = schm.load(data).data
        user = self.context.create(data)
        result = schm.dump(user).data
        self.request.response.status = 201
        return result
