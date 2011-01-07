"""Common error wrappers."""


class CloudException(Exception):
    """Base cloud exception."""
    pass


class NoContainerException(CloudException):
    """No container found."""
    pass


class NoObjectException(CloudException):
    """No storage object found."""
    pass
