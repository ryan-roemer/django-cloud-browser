"""Cloud abstractions and helpers."""
# TODO: Add RetryPolicy class.

import os

from django.core.exceptions import ImproperlyConfigured


class Config(object):
    """Cloud configuration."""
    __singleton = None

    def __init__(self, account, secret_key, rs_servicenet=False):
        """Initializer."""
        self.account = account
        self.secret_key = secret_key
        self.rs_servicenet = rs_servicenet

        self.__rs_conn_set = False
        self.__rs_conn = None

    @property
    def connection(self):
        """Return Rackspace connection object."""
        import cloudfiles as cf

        if not self.__rs_conn_set:
            kwargs = {
                'username': self.account,
                'api_key': self.secret_key,
            }

            # Only add kwarg for servicenet if True because user could set
            # environment variable 'RACKSPACE_SERVICENET' separately.
            if self.rs_servicenet:
                kwargs['servicenet'] = True

            self.__rs_conn = cf.get_connection(  # pylint: disable=W0142
                **kwargs)
            self.__rs_conn_set = True

        return self.__rs_conn

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from django.conf import settings

        def _get_setting(name):
            """Get setting from settings.py or environment."""
            # Prefer settings, then environment.
            value = getattr(settings, name, None)
            if not value:
                value = os.environ.get(name, None)
            return value

        account = _get_setting('CLOUD_BROWSER_RACKSPACE_ACCOUNT')
        secret_key = _get_setting('CLOUD_BROWSER_RACKSPACE_SECRET_KEY')
        servicenet = _get_setting('CLOUD_BROWSER_RACKSPACE_SERVICENET')

        if not (account and secret_key):
            raise ImproperlyConfigured("No suitable credentials found.")

        return cls(account, secret_key, servicenet)

    @classmethod
    def singleton(cls):
        """Get singleton object."""
        if cls.__singleton is None:
            cls.__singleton = cls.from_settings()
        return cls.__singleton


def get_connection():
    """Wrapper for global connection/config object."""
    return Config.singleton().connection
