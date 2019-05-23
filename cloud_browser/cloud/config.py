"""Cloud configuration."""


class Config(object):
    """General class helper to construct connection objects."""

    __connection_obj = None
    __connection_cls = None
    __connection_fn = None

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        conn_cls = conn_fn = None
        datastore = settings.CLOUD_BROWSER_DATASTORE

        if datastore == "ApacheLibcloud":
            # Try ApacheLibcloud
            from cloud_browser.cloud.apache_libcloud import ApacheLibcloudConnection

            provider = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER
            account = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_SECRET_KEY
            if provider and account and secret_key:
                conn_cls = ApacheLibcloudConnection
                conn_fn = lambda: ApacheLibcloudConnection(
                    provider, account, secret_key
                )

        if datastore == "AWS":
            # Try AWS
            from cloud_browser.cloud.aws import AwsConnection

            account = settings.CLOUD_BROWSER_AWS_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_AWS_SECRET_KEY
            if account and secret_key:
                conn_cls = AwsConnection
                conn_fn = lambda: AwsConnection(account, secret_key)

        if datastore == "Google":
            # Try Google Storage
            from cloud_browser.cloud.google import GsConnection

            account = settings.CLOUD_BROWSER_GS_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_GS_SECRET_KEY
            if account and secret_key:
                conn_cls = GsConnection
                conn_fn = lambda: GsConnection(account, secret_key)

        elif datastore == "Rackspace":
            # Try Rackspace
            account = settings.CLOUD_BROWSER_RACKSPACE_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_RACKSPACE_SECRET_KEY
            servicenet = settings.CLOUD_BROWSER_RACKSPACE_SERVICENET
            authurl = settings.CLOUD_BROWSER_RACKSPACE_AUTHURL
            if account and secret_key:
                from cloud_browser.cloud.rackspace import RackspaceConnection

                conn_cls = RackspaceConnection
                conn_fn = lambda: RackspaceConnection(
                    account, secret_key, servicenet=servicenet, authurl=authurl
                )

        elif datastore == "Filesystem":
            # Mock filesystem
            root = settings.CLOUD_BROWSER_FILESYSTEM_ROOT
            if root is not None:
                from cloud_browser.cloud.fs import FilesystemConnection

                conn_cls = FilesystemConnection
                conn_fn = lambda: FilesystemConnection(root)

        if conn_cls is None:
            raise ImproperlyConfigured(
                "No suitable credentials found for datastore: %s." % datastore
            )

        # Adjust connection function.
        conn_fn = staticmethod(conn_fn)

        # Directly cache attributes.
        cls.__connection_cls = conn_cls
        cls.__connection_fn = conn_fn

        return conn_cls, conn_fn

    @classmethod
    def get_connection_cls(cls):
        """Return connection class.

        :rtype: :class:`type`
        """
        if cls.__connection_cls is None:
            cls.__connection_cls, _ = cls.from_settings()
        return cls.__connection_cls

    @classmethod
    def get_connection(cls):
        """Return connection object.

        :rtype: :class:`cloud_browser.cloud.base.CloudConnection`
        """
        if cls.__connection_obj is None:
            if cls.__connection_fn is None:
                _, cls.__connection_fn = cls.from_settings()
            cls.__connection_obj = cls.__connection_fn()
        return cls.__connection_obj
