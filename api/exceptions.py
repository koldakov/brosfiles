from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        self.detail = detail
        self.status_code = code


class AuthenticationFailedException(BaseCustomException):
    def __init__(self, detail=None):
        if detail is None:
            detail = 'Not authenticated'
        super().__init__(detail=detail, code=status.HTTP_401_UNAUTHORIZED)
