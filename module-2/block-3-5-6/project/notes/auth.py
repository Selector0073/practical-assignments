"""
Domain 2 — Personal Notes: authentication, seeded users, settings helper.

Mirrors Flask's ``session``-based auth with Django's session framework backed
by DRF ``SessionAuthentication``. A custom DRF ``BaseAuthentication`` reads the
logged-in username out of ``request.session`` and a matching ``BasePermission``
enforces that a login exists (401 otherwise).

The Flask original kept per-user settings inside the Flask session as well; we
mirror exactly: ``language`` (default ``"uk"``) and ``notes_per_page`` (default
``5``) live in ``request.session``.
"""
from django.conf import settings as django_settings
from rest_framework import authentication, permissions
from rest_framework.exceptions import APIException


# ---------------------------------------------------------------------------
# Seeded USERS mapping.
# At least one username is the transliterated OWNER_FULL_NAME ("full_name"),
# plus a second test user matching the original spec's intent (taras).
# Format: {username: password}
# ---------------------------------------------------------------------------
USERS = {
    django_settings.OWNER_USERNAME: "secret123",
    "taras": "secret456",
}


def display_name_for(username):
    """Human-friendly name shown in the login welcome message."""
    if username == django_settings.OWNER_USERNAME:
        return django_settings.OWNER_FULL_NAME
    return username


class NotLoggedIn(APIException):
    """401 — no user is logged in for this request."""

    status_code = 401
    default_detail = "Not logged in"
    default_code = 'not_logged_in'


class InvalidCredentials(APIException):
    """401 — the login credentials do not match a seeded user."""

    status_code = 401
    default_detail = "Invalid credentials"
    default_code = 'invalid_credentials'


class SessionUserAuthentication(authentication.BaseAuthentication):
    """
    Authenticates a request based on the username stored in the Django session
    (set at login). ``request.user`` becomes a lightweight object whose
    ``get_username()`` returns the logged-in username.
    """

    def authenticate(self, request):
        username = getattr(request, 'session', None) and request.session.get('username')
        if not username:
            return None
        return (_SessionUser(username), username)

    def authenticate_header(self, request):
        return 'session'


class _SessionUser:
    is_authenticated = True

    def __init__(self, username):
        self.username = username

    def get_username(self):
        return self.username


class SessionLoginRequired(permissions.BasePermission):
    """
    Denies unauthenticated requests. Used on every Notes / settings / favorites
    endpoint so a missing session (username) yields a 401 with the spec's
    exact ``{"error": "Not logged in"}`` body.
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user is not None and getattr(user, 'is_authenticated', False)):
            raise NotLoggedIn()
        return True


# ---------------------------------------------------------------------------
# Settings helper mirroring session.get("language", "uk").
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    'language': 'uk',
    'notes_per_page': 5,
}


def get_settings(session):
    """Return the current per-user settings for the given request session,
    falling back to defaults for keys not present."""
    return {
        'language': session.get('language', DEFAULT_SETTINGS['language']),
        'notes_per_page': session.get('notes_per_page', DEFAULT_SETTINGS['notes_per_page']),
    }
