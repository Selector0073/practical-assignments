"""
Global DRF exception handler.

Converts the default ``{"detail": ...}`` error envelope produced by DRF's
built-in exceptions (and our custom APIException subclasses) into the
``{"error": ...}`` body required by the merged Flask↔DRF spec.

Where the response is a serializer validation error (a dict of field → errors)
it is left untouched.
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        data = response.data
        if isinstance(data, dict) and 'detail' in data:
            response.data = {'error': data['detail']}
    return response
