from pyramid.view import view_defaults, view_config

from stackcite.api import views
from stackcite.users import resources, schema


@view_defaults(context=resources.UserDocument, renderer='json')
class UserDocumentViews(views.BaseView):

    @view_config(request_method='GET', permission='retrieve')
    @views.managed_view
    def retrieve(self):
        schm = self.context.schema()
        user = self.context.retrieve()
        result, errors = schm.dump(user)
        return result

    @view_config(request_method='PUT', permission='update')
    @views.managed_view
    def update(self):
        pass

    @view_config(request_method='DELETE', permission='delete')
    @views.managed_view
    def delete(self):
        pass


@view_defaults(context=resources.UserCollection, renderer='json')
class UserCollectionViews(views.BaseView):

    @view_config(request_method='POST', permission='create')
    @views.managed_view
    def create(self):
        data = self.request.json_body
        schm = schema.User(strict=True, only=('id', 'email', 'password'))
        data, errors = schm.load(data)
        user = self.context.create(data)
        result, errors = schm.dump(user)
        self.request.response.status = 201
        return result

    @view_config(request_method='GET', permission='retrieve')
    @views.managed_view
    def retrieve(self):
        pass
