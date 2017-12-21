import logging
import mongoengine
from pyramid import security as sec

from stackcite.api import resources
from stackcite.users import models


_LOG = logging.getLogger(__name__)


class ConfResource(resources.APIIndexResource):

    __acl__ = [
        (sec.Allow, sec.Everyone, ('create', 'update'))
    ]

    def create(self, data):
        """
        Issues a new account confirmation token. Replaces an existing token if
        one already exists in the database.
        """
        email = data['email']
        user = models.User.objects.get(email=email)
        token = models.ConfirmToken.new(user)
        try:
            token.save()
        except mongoengine.NotUniqueError:
            models.ConfirmToken.objects(_user=user).delete()
            token.save()
        _LOG.info('Confirmation key: {} {}'.format(user.email, token.key))
        return token

    def update(self, data):
        """
        Confirms a user's registration.
        """
        key = data['key']
        token = models.ConfirmToken.objects.get(_key=key)
        user = token.confirm_user()
        _LOG.info('Confirmation key: {} {}'.format(user.email, token.key))
        return token
