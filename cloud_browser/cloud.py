"""Cloud abstractions and helpers."""
# TODO: Add RetryPolicy class.

import os

from django.core.exceptions import ImproperlyConfigured

from cloud_browser.common import SEP, path_join, basename

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


class CloudObject(object):
    """Cloud object wrapper."""
    class Types(object):
        FILE = 'file'
        SUBDIR = 'subdirectory'
    
    def __init__(self, container, name, bytes=0, content_type='',
            last_modified=None, obj_type=None):
        """Initializer."""
        self.container = container
        self.name = name.rstrip(SEP)
        self.bytes = bytes
        self.content_type = content_type
        self.last_modified = last_modified
        self.type = obj_type or self.Types.FILE

    @property
    def is_subdir(self):
        """Is a subdirectory?"""
        return self.type == self.Types.SUBDIR
    
    @property
    def is_file(self):
        """Is a file object?"""
        return self.type == self.Types.FILE
    
    @property
    def path(self):
        """Full path (including container)."""
        return path_join(self.container.name, self.name)

    @property
    def basename(self):
        """Base name from rightmost separator."""
        return basename(self.name)

    @classmethod
    def from_info(cls, container, info_obj):
        """Create from subdirectory or file info object."""
        create_fn = cls.from_subdir if 'subdir' in info_obj \
            else cls.from_file_info
        return create_fn(container, info_obj)

    @classmethod
    def from_subdir(cls, container, info_obj):
        """Create from subdirectory info object."""
        return cls(container, info_obj['subdir'], obj_type=cls.Types.SUBDIR)

    @classmethod
    def from_file_info(cls, container, info_obj):
        """Create from regular info object."""
        return cls(container,
                   info_obj['name'],
                   info_obj['bytes'],
                   info_obj['content_type'],
                   info_obj['last_modified'],
                   cls.Types.FILE)
