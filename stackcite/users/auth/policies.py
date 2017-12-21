from zope.interface import implementer

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import (
    CallbackAuthenticationPolicy,
    Everyone,
    Authenticated
)

from . import utils


@implementer(IAuthenticationPolicy)
class AuthTokenAuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    A custom REST authentication policy that evaluates an `api_key` provided in
    the request header against those saved in the database.
    """

    def __init__(self, callback=None, debug=False):
        self.callback = callback or utils.get_groups
        self.debug = debug

    def authenticated_userid(self, request):
        """
        Resolves a :class:`stackcite.AuthToken` key to retrieve the
        :class:`bson.ObjectId` of a :class:`stackcite.User`. If the token
        does not exist, method returns `None`.
        """
        if request.user:
            return str(request.user.id)

    def effective_principals(self, request):
        """
        Resolves the effective principles of a :class:`stackcite.User`.
        """
        principals = [Everyone]
        user = request.user
        if user is not None:
            principals.append(Authenticated)
            principals.append(str(user.id))
            principals.extend(user.groups)
        return principals
