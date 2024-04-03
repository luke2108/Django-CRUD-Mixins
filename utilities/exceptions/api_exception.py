from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import (
    APIException,
    NotFound,
    ValidationError,
    status,
)
from rest_framework.views import exception_handler

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404


class ObjectDoesNotExistError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Object not found"
    default_code = "not_found"


class StatusError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad status"
    default_code = "bad_status"


class InternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error"
    default_code = "server_error"


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    default_code = "bad_request"


class DeleteRelatedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This data is related some data"
    default_code = "delete_related_error"


class UserWhitelistEmailError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "user_whitelist_email_error"


class CmsImageFileTooLargeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "cms_image_download_error"


class KannaApiError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "kanna_api_error"

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code:
            self.status_code = status_code
        super().__init__(detail, code)


class WhitelistError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Email address is not whitelisted"
    default_code = "whitelist_error"


class UserConstuctionError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "construction was used"


def custom_exception_handler(exc, context):
    # DjangoのValidationErrorをDRFのValidationErrorに変換
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail=exc.messages)

    # PydanticのValidationErrorをDRFのValidationErrorに変換
    if isinstance(exc, PydanticValidationError):
        exc = ValidationError(detail=exc.raw_errors)

    # Http404をNotFoundに変換
    if isinstance(exc, Http404):
        exc = NotFound()

    if isinstance(exc, ObjectDoesNotExist):
        exc = ObjectDoesNotExistError()
    # else:
    #     exc = InternalServerError()

    response = exception_handler(exc, context)
    if not response:
        return None

    response.data = {
        "code": getattr(exc, "code", exc.default_code),
        "detail": getattr(exc, "detail", exc.default_detail),
    }
    response.exc = exc

    return response
