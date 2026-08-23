"""
Domain 1 (Task Manager) custom DRF exceptions.

DRF lets us raise typed exceptions from authentication/permission code and
inside views; a global exception handler (see ``config.exceptions``) converts
the ``detail`` into the exact ``{"error": ...}`` body required by the spec.
"""
from rest_framework.exceptions import APIException


class MissingXUser(APIException):
    """401 — the X-User header is required but was not supplied."""

    status_code = 401
    default_detail = "Header 'X-User' is required"
    default_code = 'missing_x_user'


class ForbiddenTask(APIException):
    """403 — the caller may only delete their own tasks."""

    status_code = 403
    default_detail = "You can only delete your own tasks"
    default_code = 'forbidden_task'
