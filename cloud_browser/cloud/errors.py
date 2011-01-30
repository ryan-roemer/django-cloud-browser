"""Common cloud error wrappers."""
import sys

from functools import wraps


class CloudException(Exception):
    """Base cloud exception."""
    pass


class InvalidNameException(CloudException):
    """Bad name."""
    pass


class NotPermittedException(CloudException):
    """Access is not permitted"""
    pass


class NoContainerException(CloudException):
    """No container found."""
    pass


class NoObjectException(CloudException):
    """No storage object found."""
    pass


class CloudExceptionWrapper(object):
    """Exception translator.

    This class wraps a "real" underlying cloud class exception and translates
    it to a "common" exception class from this module. The exception stack
    from the wrapped exception is preserved through some :meth:`sys.exc_info`
    hackery.

    It is implemented as a decorator such that you can do something like::

        class MyWrapper(CloudExceptionWrapper):
            '''Convert exception to another one.'''
            translations = { Exception: NotImplementedError }

        @MyWrapper()
        def foo():
            raise Exception("Hi.")

        foo()

    The alternate way is to handle the translations directly in a member
    function::

        class MyWrapper(CloudExceptionWrapper):
            '''Convert exception to another one.'''
            def translate(self, exc):
                if isinstance(exc, Exception):
                    return NotImplementedError

                return None

        @MyWrapper()
        def foo():
            raise Exception("Hi.")

        foo()

    which produces output like::

        Traceback (most recent call last):
          File "...", line ..., in <module>
            foo()
          File "...", line ..., in wrapped
            return operation(*args, **kwargs)
          File "...", line ..., in foo
            raise Exception("Hi.")
        NotImplementedError: Hi.

    So, we can see that we get a different exception with the proper stack.

    Overriding classes should implement the ``translations`` class variable
    dictionary for translating an underlying library exception to a class
    in this module. See any of the data implementation modules for examples.
    """
    translations = {}
    _excepts = None

    def __new__(cls, *args, **kwargs):
        """New."""
        obj = object.__new__(cls, *args, **kwargs)

        # Patch in lazy translations.
        if not obj.translations:
            lazy_translations = cls.lazy_translations()
            if lazy_translations:
                obj.translations = lazy_translations

        return obj

    @classmethod
    def excepts(cls):
        """Return tuple of underlying exception classes to trap and wrap.

        :rtype: ``tuple`` of ``type``
        """
        if cls._excepts is None:
            cls._excepts = tuple(cls.translations.keys())
        return cls._excepts

    def translate(self, exc):
        """Return translation of exception to new class.

        Calling code should only raise exception if exception class is passed
        in, else ``None`` (which signifies no wrapping should be done).
        """
        # Find actual class.
        for key in self.translations.keys():
            if isinstance(exc, key):
                return self.translations[key](unicode(exc))

        return None

    def __call__(self, operation):
        """Call and wrap exceptions."""

        @wraps(operation)
        def wrapped(*args, **kwargs):
            """Wrapped function."""

            try:
                return operation(*args, **kwargs)
            except self.excepts(), exc:
                new_exc = self.translate(exc)
                if new_exc:
                    # Wrap and raise with stack intact.
                    raise new_exc.__class__, new_exc, sys.exc_info()[2]
                else:
                    raise

        return wrapped

    @classmethod
    def lazy_translations(cls):
        """Lazy translations definitions (for additional checks)."""
        return None
