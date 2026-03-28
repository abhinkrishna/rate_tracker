from rest_framework import status
from rest_framework.response import Response


class _SuccessResponse:
    def __init__(
        self, message="Success", code="success", http_status=status.HTTP_200_OK
    ):
        self.message = message
        self.code = code
        self.http_status = http_status

    def to_response(self, data=None, message=None, code=None):
        response_data = {
            "code": code or self.code,
            "status": self.http_status,
            "success": True,
            "message": message or self.message,
            "data": data,
        }
        return Response(response_data, status=self.http_status)


class _ErrorResponse:
    def __init__(self, message, code, http_status):
        self.message = message
        self.code = code
        self.http_status = http_status

    def to_response(self, message=None, data=None, code=None):
        return Response(
            {
                "code": code or self.code,
                "status": self.http_status,
                "success": False,
                "message": message or self.message,
                "data": data,
            },
            status=self.http_status,
        )


class SUCCESS_RESPONSE:
    CREATED = _SuccessResponse(
        message="Resource created successfully.",
        code="created",
        http_status=status.HTTP_201_CREATED,
    )
    OK = _SuccessResponse(
        message="Resource retrieved successfully.",
        code="ok",
        http_status=status.HTTP_200_OK,
    )
    ACCEPTED = _SuccessResponse(
        message="Request accepted successfully.",
        code="accepted",
        http_status=status.HTTP_202_ACCEPTED,
    )
    DELETED = _SuccessResponse(
        message="Resource deleted successfully.",
        code="deleted",
        http_status=status.HTTP_202_ACCEPTED,
    )


class ERROR_RESPONSE:
    BAD_REQUEST = _ErrorResponse(
        "The request is invalid.", "bad_request", status.HTTP_400_BAD_REQUEST
    )
    UNAUTHORIZED = _ErrorResponse(
        "Authentication credentials were not provided or are invalid.",
        "unauthorized",
        status.HTTP_401_UNAUTHORIZED,
    )
    FORBIDDEN = _ErrorResponse(
        "You do not have permission to perform this action.",
        "forbidden",
        status.HTTP_403_FORBIDDEN,
    )
    NOT_FOUND = _ErrorResponse(
        "The requested resource was not found.",
        "not_found",
        status.HTTP_404_NOT_FOUND,
    )
    SERVER_ERROR = _ErrorResponse(
        "An internal server error occurred.",
        "server_error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    METHOD_NOT_ALLOWED = _ErrorResponse(
        "Method not allowed.",
        "method_not_allowed",
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )
    UNPROCESSABLE_ENTITY = _ErrorResponse(
        "Unable to process the request.",
        "unprocessable_entity",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
