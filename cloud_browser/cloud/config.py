"""Cloud configuration."""


class Config(object):
    """Cloud configuration helper."""
    __singleton = None

    def __init__(self, connection):
        """Initializer."""
        self.connection = connection

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        conn = None
        if conn is None:
            # Try Rackspace
            account = settings.CLOUD_BROWSER_RACKSPACE_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_RACKSPACE_SECRET_KEY
            servicenet = settings.CLOUD_BROWSER_RACKSPACE_SERVICENET
            if (account and secret_key):
                from cloud_browser.cloud.rackspace import RackspaceConnection
                conn = RackspaceConnection(account, secret_key, servicenet)

        if not conn:
            raise ImproperlyConfigured("No suitable credentials found.")

        return cls(conn)

    @classmethod
    def singleton(cls):
        """Get singleton object."""
        if cls.__singleton is None:
            cls.__singleton = cls.from_settings()
        return cls.__singleton
