class UUID4HEXNotGenerated(Exception):
    pass


class SafeRandomStringNotGenerated(Exception):
    """Random string is not generated"""


class NotAllowed(Exception):
    """Action in view is not allowed"""
