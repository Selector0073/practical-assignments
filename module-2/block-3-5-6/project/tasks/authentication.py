"""
Custom header-based authentication for the Task Manager domain.

The original Flask spec used a custom ``X-User`` header to identify the current
user. In DRF this maps to a custom :class:`BaseAuthentication` subclass (how
the header is *read*) plus a :class:`BasePermission` subclass (how the caller
is *authorized*). Both are reusable across the "my tasks" and "delete task"
endpoints.
"""
from rest_framework import authentication
from rest_framework import permissions


class XUserHeaderError(Exception):
    """Raised internally when the X-User header is missing on an endpoint
    that requires it. Value is the JSON error body and the exact status to
    return (mirroring the Flask error contract)."""

    def __init__(self, message, status):
        self.message = message
        self.status = status
        super().__init__(message)


class MissingXUserHeader(XUserHeaderError):
    def __init__(self):
        super().__init__(
            "Header 'X-User' is required", 401
        )


class XUserAuthentication(authentication.BaseAuthentication):
    """
    Reads the ``X-User`` header and exposes it as the "authenticated" user.

    ``request.user`` will be a small object whose ``get_username()`` method
    returns the header value. If the header is missing and the endpoint
    configured ``XUserPermission`` as its ``permission_classes``, that
    permission class will issue the 401.
    """

    header = 'X-User'

    def authenticate(self, request):
        user = request.headers.get(self.header)
        if user is None:
            return None
        return (_XUser(user), user)

    def authenticate_header(self, request):
        return self.header


class _XUser:
    """Minimal stand-in user object carrying the X-User value."""

    is_authenticated = True

    def __init__(self, name):
        self.name = name

    def get_username(self):
        return self.name


class XUserPermission(permissions.BasePermission):
    """
    Raises a 401 when the ``X-User`` header is missing.

    Used (together with :class:`XUserAuthentication`) on endpoints that
    identity-based authorization through the header.
    """

    message = "Header 'X-User' is required"

    def has_permission(self, request, view):
        if request.user is None or not getattr(request.user, 'is_authenticated', False):
            return False
        if not getattr(request.user, 'name', None):
            return False
        return True
