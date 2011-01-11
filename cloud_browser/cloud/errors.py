"""Common error wrappers."""
import sys


class CloudException(Exception):
    """Base cloud exception."""
    pass


class InvalidNameException(CloudException):
    """Bad name."""
    pass


class NoContainerException(CloudException):
    """No container found."""
    pass


class NoObjectException(CloudException):
    """No storage object found."""
    pass


class CloudExceptionWrapper(object):
    """Exception translator."""
    translations = {}
    _excepts = None

    @classmethod
    def excepts(cls):
        """Exception tuple."""
        if cls._excepts is None:
            cls._excepts = tuple(cls.translations.keys())
        return cls._excepts

    def __call__(self, operation):
        """Call and wrap exceptions."""

        def wrapped(*args, **kwargs):
            """Wrapped function."""

            try:
                return operation(*args, **kwargs)
            except self.excepts(), exc:
                # Find actual class.
                key_cls = None
                for key in self.translations.keys():
                    if isinstance(exc, key):
                        key_cls = key
                        break

                # Wrap and raise with stack intact.
                new_exc = self.translations[key_cls](unicode(exc))
                raise new_exc.__class__, new_exc, sys.exc_info()[2]

        return wrapped
