"""Cloud abstractions and helpers."""
import mimetypes

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
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        account = settings.CLOUD_BROWSER_RACKSPACE_ACCOUNT
        secret_key = settings.CLOUD_BROWSER_RACKSPACE_SECRET_KEY
        servicenet = settings.CLOUD_BROWSER_RACKSPACE_SERVICENET

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

    def __init__(self, container, name, **kwargs):
        """Initializer.

        :param container: Container object.
        :param name: Object name / path.
        :kwarg bytes: Number of bytes in object.
        :kwarg content_type: Document 'content-type'.
        :kwarg last_modified: Last modified date.
        :kwarg obj_type: Type of object (e.g., file or subdirectory).
        """
        self.container = container
        self.name = name.rstrip(SEP)
        self.bytes = kwargs.get('bytes', 0)
        self.content_type = kwargs.get('content_type', '')
        self.content_encoding = None  # RS has no content encoding.
        self.last_modified = kwargs.get('last_modified', None)
        self.type = kwargs.get('obj_type', self.Types.FILE)

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

    @property
    def smart_content_type(self):
        """Smart content type."""
        content_type = self.content_type
        if content_type in (None, '', 'application/octet-stream'):
            content_type, _ = mimetypes.guess_type(self.name)

        return content_type

    @property
    def smart_content_encoding(self):
        """Smart content encoding."""
        encoding = self.content_encoding
        if not encoding:
            base_list = self.basename.split('.')
            while (not encoding) and len(base_list) > 1:
                _, encoding = mimetypes.guess_type('.'.join(base_list))
                base_list.pop()

        return encoding

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
                   name=info_obj['name'],
                   bytes=info_obj['bytes'],
                   content_type=info_obj['content_type'],
                   last_modified=info_obj['last_modified'],
                   obj_type=cls.Types.FILE)

    @classmethod
    def from_obj(cls, container, file_obj):
        """Create from regular info object."""
        return cls(container,
                   name=file_obj.name,
                   bytes=file_obj.size,
                   content_type=file_obj.content_type,
                   last_modified=file_obj.last_modified,
                   obj_type=cls.Types.FILE)
