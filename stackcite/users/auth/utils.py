import os
import hashlib
import mongoengine

from mongoengine import context_managers, InvalidDocumentError

from stackcite.users import models
from stackcite.api.validators import keys


def gen_key():
    """
    Generates a cryptographic key used for API Tokens and account confirmation.
    """
    return hashlib.sha224(os.urandom(128)).hexdigest()


def get_token(request):
    """
    Returns a token key from the request authorization header. The header must
    take the following form:

    `Authentication: key [token]`
    """

    try:
        auth_type, key = request.authorization
        if auth_type.lower() == 'key' and keys.validate_key(key):
            token = models.AuthToken.objects.get(_key=key)
            return token
    except (ValueError, TypeError, InvalidDocumentError):
        return None


def get_user(request):
    """
    Returns a user based on an API key located in the request header.
    """

    try:
        if request.token:
            with context_managers.no_dereference(request.token) as token:
                return token.user
    except (ValueError, TypeError, mongoengine.DoesNotExist):
        return None


def get_groups(user_id, request):
    """
    Returns a list of groups for the current user if `user_id` matches the `id`
    field of the current request's :class:`stackcite.User`.
    """

    return request.user.groups if request.user.id == user_id else []
