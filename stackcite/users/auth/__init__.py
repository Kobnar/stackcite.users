from stackcite.api import auth as _auth

from .utils import get_token, get_user
from .policies import AuthTokenAuthenticationPolicy


GROUP_CHOICES = _auth.GROUP_CHOICES
GROUPS = _auth.GROUPS
USERS = _auth.USERS
STAFF = _auth.STAFF
ADMIN = _auth.ADMIN
