from stackcite.api import exceptions as _exc


StackciteError = _exc.StackciteError


class AuthenticationError(StackciteError):
    """
    A custom exception raised when authentication fails for whatever reason.
    """

    _DEFAULT_MESSAGE = 'Authentication failed'
