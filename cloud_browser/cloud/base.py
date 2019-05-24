"""Cloud datastore API base abstraction."""
import mimetypes

from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors
from cloud_browser.common import SEP, basename, path_join


class CloudObjectTypes(object):
    """Cloud object types helper."""

    FILE = "file"
    SUBDIR = "subdirectory"


class CloudObject(object):
    """Cloud object wrapper."""

    type_cls = CloudObjectTypes

    def __init__(self, container, name, **kwargs):
        """Initializer.

        :param container: Container object.
        :param name: Object name / path.
        :kwarg size: Number of bytes in object.
        :kwarg content_type: Document 'content-type'.
        :kwarg content_encoding: Document 'content-encoding'.
        :kwarg last_modified: Last modified date.
        :kwarg obj_type: Type of object (e.g., file or subdirectory).
        """
        self.container = container
        self.name = name.rstrip(SEP)
        self.size = kwargs.get("size", 0)
        self.content_type = kwargs.get("content_type", "")
        self.content_encoding = kwargs.get("content_encoding", "")
        self.last_modified = kwargs.get("last_modified", None)
        self.type = kwargs.get("obj_type", self.type_cls.FILE)
        self.__native = None

    @property
    def native_obj(self):
        """Native storage object."""
        if self.__native is None:
            self.__native = self._get_object()

        return self.__native

    def _get_object(self):
        """Return native storage object."""
        raise NotImplementedError

    @property
    def is_subdir(self):
        """Is a subdirectory?"""
        return self.type == self.type_cls.SUBDIR

    @property
    def is_file(self):
        """Is a file object?"""
        return self.type == self.type_cls.FILE

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
        if content_type in (None, "", "application/octet-stream"):
            content_type, _ = mimetypes.guess_type(self.name)

        return content_type

    @property
    def smart_content_encoding(self):
        """Smart content encoding."""
        encoding = self.content_encoding
        if not encoding:
            base_list = self.basename.split(".")
            while (not encoding) and len(base_list) > 1:
                _, encoding = mimetypes.guess_type(".".join(base_list))
                base_list.pop()

        return encoding

    def read(self):
        """Return contents of object."""
        return self._read()

    def _read(self):
        """Return contents of object."""
        raise NotImplementedError


class CloudContainer(object):
    """Cloud container wrapper."""

    #: Storage object child class.
    obj_cls = CloudObject

    #: Maximum number of objects that can be listed or ``None``.
    max_list = None

    def __init__(self, conn, name=None, count=None, size=None):
        """Initializer."""
        self.conn = conn
        self.name = name
        self.count = count
        self.size = size
        self.__native = None

    @property
    def native_container(self):
        """Native container object."""
        if self.__native is None:
            self.__native = self._get_container()

        return self.__native

    def _get_container(self):
        """Return native container object."""
        raise NotImplementedError

    def get_objects(
        self, path, marker=None, limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT
    ):
        """Get objects."""
        raise NotImplementedError

    def get_object(self, path):
        """Get single object."""
        raise NotImplementedError


class CloudConnection(object):
    """Cloud connection wrapper."""

    #: Container child class.
    cont_cls = CloudContainer

    #: Maximum number of containers that can be listed or ``None``.
    max_list = None

    def __init__(self, account, secret_key):
        """Initializer."""
        self.account = account
        self.secret_key = secret_key
        self.__native = None

    @property
    def native_conn(self):
        """Native connection object."""
        if self.__native is None:
            self.__native = self._get_connection()

        return self.__native

    def _get_connection(self):
        """Return native connection object."""
        raise NotImplementedError

    def get_containers(self):
        """Return available containers."""
        permitted = lambda c: settings.container_permitted(c.name)
        return [c for c in self._get_containers() if permitted(c)]

    def _get_containers(self):
        """Return available containers."""
        raise NotImplementedError

    def get_container(self, path):
        """Return single container."""
        if not settings.container_permitted(path):
            raise errors.NotPermittedException(
                'Access to container "%s" is not permitted.' % path
            )
        return self._get_container(path)

    def _get_container(self, path):
        """Return single container."""
        raise NotImplementedError
