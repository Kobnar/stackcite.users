from mongoengine import context_managers
from pyramid.view import view_defaults, view_config

from stackcite.api import views, exceptions as exc
from stackcite.users import auth, models, resources, schema


@view_defaults(context=resources.ConfirmResource, renderer='json')
class ConfirmationViews(views.BaseView):

    @view_config(request_method='POST')
    @views.managed_view
    def create(self):
        data = self.request.json_body
        schm = schema.CreateConfirmationToken(strict=True)
        data = schm.load(data).data

        # Forbid creating new tokens for confirmed users
        user = models.User.objects.get(email=data['email'])
        if auth.USERS in user.groups:
            msg = 'User is already confirmed.'
            raise exc.APIForbidden(detail=msg)

        self.context.create(data)
        self.request.response.status_code = 201

    @view_config(request_method='PUT')
    @views.managed_view
    def update(self):
        data = self.request.json_body
        schm = schema.UpdateConfirmationToken(strict=True)
        data = schm.load(data).data
        conf_token = self.context.update(data)
        with context_managers.no_dereference(models.ConfirmToken):
            return {
                'user': {
                    'id': str(conf_token.user.id)
                }
            }
