from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from rate_tracker.settings import DEBUG

from rate_tracker.response import ERROR_RESPONSE


def custom_exception_handler(exc, context):
    """
    Global exception handler:
    - Keeps serializer validation errors intact
    - Wraps all other framework errors in FitSuite error format
    """

    response = drf_exception_handler(exc, context)

    # Unhandled exception → 500
    if response is None:
        if DEBUG:
            raise exc
        return ERROR_RESPONSE.SERVER_ERROR.to_response()

    status_code = response.status_code

    error_map = {
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE.BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE.UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE.FORBIDDEN,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE.NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR: ERROR_RESPONSE.SERVER_ERROR,
    }

    error = error_map.get(status_code, ERROR_RESPONSE.SERVER_ERROR)

    return error.to_response(data=response.data)
