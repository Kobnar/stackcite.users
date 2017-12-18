from stackcite import exceptions as exc


class AuthenticationError(exc.StackciteError):
    """
    A custom exception raised when authentication fails for whatever reason.
    """

    _DEFAULT_MESSAGE = 'Authentication failed'
