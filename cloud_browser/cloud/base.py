"""Cloud API base abstraction."""
import cloudfiles as cf
import mimetypes
import sys

from cloud_browser.cloud import errors
from cloud_browser.common import SEP, path_join, basename


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


class RackspaceExceptionWrapper(CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        cf.errors.NoSuchContainer: errors.NoContainerException,
        cf.errors.NoSuchObject: errors.NoObjectException,
    }
wrap_rs_errors = RackspaceExceptionWrapper()  # pylint: disable=C0103


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
        :kwarg content_encoding: Document 'content-encoding'.
        :kwarg last_modified: Last modified date.
        :kwarg obj_type: Type of object (e.g., file or subdirectory).
        """
        self.container = container
        self.name = name.rstrip(SEP)
        self.bytes = kwargs.get('bytes', 0)
        self.content_type = kwargs.get('content_type', '')
        self.content_encoding = kwargs.get('content_encoding', '')
        self.last_modified = kwargs.get('last_modified', None)
        self.type = kwargs.get('obj_type', self.Types.FILE)
        self.__native = None

    @property
    @wrap_rs_errors
    def native_obj(self):
        """Return native storage object."""
        if self.__native is None:
            self.__native = \
                self.container.native_container.get_object(self.name)

        return self.__native

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

    @wrap_rs_errors
    def read(self):
        """Return contents of object."""
        return self.native_obj.read()

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


# TODO: Wrap rs exceptions.
class CloudContainer(object):
    """Cloud object wrapper."""
    obj_cls = CloudObject

    def __init__(self, conn, name=None, count=None, size=None):
        """Initializer."""
        self.conn = conn
        self.name = name
        self.count = count
        self.size = size
        self.__native = None

    @property
    @wrap_rs_errors
    def native_container(self):
        """Native container object."""
        if self.__native is None:
            self.__native = self.conn.native_conn.get_container(self.name)

        return self.__native

    # TODO: set limit to DEFAULT_LIMIT
    @wrap_rs_errors
    def get_objects(self, path, marker=None, limit=20):
        """Get objects."""
        path = path + SEP if path else ''
        object_infos = self.native_container.list_objects_info(
            limit=limit, delimiter=SEP, prefix=path, marker=marker)

        return [self.obj_cls.from_info(self, x) for x in object_infos]

    @wrap_rs_errors
    def get_object(self, path):
        """Get single object."""
        obj = self.native_container.get_object(path)
        return self.obj_cls.from_obj(self, obj)


class CloudConnection(object):
    """Cloud connection abstraction."""
    cont_cls = CloudContainer

    def __init__(self, account, secret_key, rs_servicenet=False):
        """Initializer."""
        self.account = account
        self.secret_key = secret_key
        self.rs_servicenet = rs_servicenet
        self.__native = None

    @property
    def native_conn(self):
        """Return native connection object."""
        if self.__native is None:
            self.__native = self._get_connection()

        return self.__native

    @wrap_rs_errors
    def _get_connection(self):
        """Return native connection object."""
        kwargs = {
            'username': self.account,
            'api_key': self.secret_key,
        }

        # Only add kwarg for servicenet if True because user could set
        # environment variable 'RACKSPACE_SERVICENET' separately.
        if self.rs_servicenet:
            kwargs['servicenet'] = True

        return cf.get_connection(**kwargs)  # pylint: disable=W0142

    @wrap_rs_errors
    def get_containers(self):
        """Return available containers."""
        infos = self.native_conn.list_containers_info()
        return [self.cont_cls(self, i['name'], i['count'], i['bytes'])
                for i in infos]

    @wrap_rs_errors
    def get_container(self, path):
        """Return single container."""
        cont = self.native_conn.get_container(path)
        return self.cont_cls(self,
                             cont.name,
                             cont.object_count,
                             cont.size_used)
