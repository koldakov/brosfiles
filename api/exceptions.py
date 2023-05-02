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


class FeatureNotReady(BaseCustomException):
    def __init__(self, detail=None):
        if detail is None:
            detail = 'Not implemented'
        # Should be ``status.HTTP_501_NOT_IMPLEMENTED``, but webhook requires 200-299 response code.
        super().__init__(detail=detail, code=status.HTTP_200_OK)


class UserAlreadyExists(BaseCustomException):
    def __init__(self, detail=None):
        if detail is None:
            detail = 'User already exists'

        super().__init__(detail=detail, code=status.HTTP_400_BAD_REQUEST)
