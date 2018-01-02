import functools

from stackcite.api import views as api_views, exceptions as api_exc
from stackcite.users import exceptions as exc


def managed_view(view_method):

    # Wrap upstream manager
    view_method = api_views.managed_view(view_method)

    @functools.wraps(view_method)
    def wrapper(self, *args, **kwargs):
        try:
            return view_method(self, *args, **kwargs)

        except exc.AuthenticationError:
            raise api_exc.APIAuthenticationFailed()

    return wrapper
