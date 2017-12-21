from mongoengine import context_managers
from pyramid.view import view_defaults, view_config

from stackcite.api import views, exceptions
from stackcite.users import models, resources, schema


@view_defaults(context=resources.ConfResource, renderer='json')
class ConfirmationViews(views.BaseView):

    @view_config(request_method='POST')
    @views.managed_view
    def create(self):
        data = self.request.json_body
        schm = schema.CreateConfirmationToken()
        data, errors = schm.load(data)
        self.context.create(data)
        return exceptions.APINoContent()

    @view_config(request_method='PUT')
    @views.managed_view
    def update(self):
        data = self.request.json_body
        schm = schema.UpdateConfirmationToken()
        data, errors = schm.load(data)
        conf_token = self.context.update(data)
        with context_managers.no_dereference(models.ConfirmToken):
            return {
                'user': {
                    'id': str(conf_token.user.id)
                }
            }
