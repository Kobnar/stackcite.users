from pyramid import security as sec

from stackcite.api import resources
from stackcite.users import models, schema


class AuthResource(resources.APIIndexResource):

    __acl__ = [
        (sec.Allow, sec.Authenticated, ('retrieve', 'update', 'delete')),
        (sec.Allow, sec.Everyone, 'create'),
        sec.DENY_ALL
    ]

    def create(self, data):
        """
        Creates or updates a :class:`~AuthToken` based on valid user
        authentication credentials.

        NOTE: "key" in  this context refers to a :class:`~ConfirmToken` key,
        not a :class:`~AuthToken` key.
        """
        email = data.get('email')
        password = data.get('password')
        user = models.User.authenticate(email, password)
        token = models.AuthToken(_user=user)
        token.save()
        user.touch_login()
        user.save()
        return token

    def retrieve(self, token):
        """
        Confirms the existence of a :class:`~AuthToken`.
        """
        return token

    def update(self, token):
        """
        Updates an existing :class:`~AuthToken`.
        """
        token.save()
        return token

    def delete(self, token):
        """
        Deletes an existing :class:`~AuthToken`.
        """
        if token:
            token.delete()
            return True
        else:
            return False
