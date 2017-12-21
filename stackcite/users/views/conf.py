from mongoengine import context_managers
from pyramid.view import view_defaults

from stackcite.api import views, exceptions
from stackcite.users import data as db, schema


@view_defaults(renderer='json')
class ConfirmationViews(views.BaseView):

    METHODS = {
        'POST': 'create',
        'PUT': 'update',
    }

    @views.managed_view
    def create(self):
        data = self.request.json_body
        schm = schema.CreateConfirmationToken()
        data, errors = schm.load(data)
        self.context.create(data)
        return exceptions.APINoContent()

    @views.managed_view
    def update(self):
        data = self.request.json_body
        schm = schema.UpdateConfirmationToken()
        data, errors = schm.load(data)
        conf_token = self.context.update(data)
        with context_managers.no_dereference(db.ConfirmToken):
            return {
                'user': {
                    'id': str(conf_token.user.id)
                }
            }
