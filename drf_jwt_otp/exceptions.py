from rest_framework.exceptions import APIException


class IsOtpUserException(APIException):
    status_code = 401
