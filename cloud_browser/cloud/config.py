"""Cloud configuration."""
from cloud_browser.cloud.base import CloudConnection


class Config(object):
    """Cloud configuration helper."""
    conn_cls = CloudConnection
    __singleton = None

    def __init__(self, connection):
        """Initializer."""
        self.connection = connection

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        account = settings.CLOUD_BROWSER_RACKSPACE_ACCOUNT
        secret_key = settings.CLOUD_BROWSER_RACKSPACE_SECRET_KEY
        servicenet = settings.CLOUD_BROWSER_RACKSPACE_SERVICENET

        if not (account and secret_key):
            raise ImproperlyConfigured("No suitable credentials found.")

        conn = cls.conn_cls(account, secret_key, servicenet)
        return cls(conn)

    @classmethod
    def singleton(cls):
        """Get singleton object."""
        if cls.__singleton is None:
            cls.__singleton = cls.from_settings()
        return cls.__singleton
