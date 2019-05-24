"""ApacheLibcloud datastore."""
from datetime import datetime
from io import BytesIO
from itertools import islice

from cloud_browser.app_settings import settings
from cloud_browser.cloud import base, errors
from cloud_browser.common import SEP, requires

###############################################################################
# Constants / Conditional Imports
###############################################################################
try:
    import libcloud  # pylint: disable=F0401
except ImportError:
    libcloud = None  # pylint: disable=C0103

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"


###############################################################################
# Classes
###############################################################################
class ApacheLibcloudExceptionWrapper(errors.CloudExceptionWrapper):
    """ApacheLibcloud :mod:`cloudfiles` exception translator."""

    @classmethod
    @requires(libcloud, "libcloud")
    def lazy_translations(cls):
        """Lazy translations."""

        types = libcloud.storage.types

        return {
            types.ContainerDoesNotExistError: errors.NoContainerException,
            types.ObjectDoesNotExistError: errors.NoObjectException,
        }


class ApacheLibcloudObject(base.CloudObject):
    """ApacheLibcloud object wrapper."""

    def _get_object(self):
        """Return native storage object."""
        return self.container.native_container.get_object(self.name)

    def _read(self):
        """Return contents of object."""
        stream = self.native_obj.as_stream()
        content = BytesIO()
        content.writelines(stream)
        content.seek(0)
        return content.read()

    @classmethod
    def from_libcloud(cls, container, obj):
        """Create object from `libcloud.storage.base.Object`."""

        try:
            last_modified = obj.extra["last_modified"]
            last_modified = datetime.strptime(last_modified, DATE_FORMAT)
        except (KeyError, ValueError):
            last_modified = None

        return cls(
            container,
            name=obj.name,
            size=obj.size,
            content_encoding=obj.extra.get("content_encoding"),
            content_type=obj.extra.get("content_type"),
            last_modified=last_modified,
            obj_type=cls.type_cls.FILE,
        )


class ApacheLibcloudContainer(base.CloudContainer):
    """ApacheLibcloud container wrapper."""

    #: Storage object child class.
    obj_cls = ApacheLibcloudObject

    #: Exception translations.
    wrap_libcloud_errors = ApacheLibcloudExceptionWrapper()

    def _get_container(self):
        """Return native container object."""
        return self.conn.native_conn.get_container(self.name)

    @wrap_libcloud_errors
    def get_objects(
        self, path, marker=None, limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT
    ):
        """Get objects."""
        client = self.conn.native_conn
        path = path.rstrip(SEP) + SEP if path else ""
        dirs = set()

        def get_files_and_directories(items):
            for item in items:
                suffix = item.name[len(path) :]
                subdirs = suffix.split(SEP)
                is_file = len(subdirs) == 1

                if is_file:
                    yield self.obj_cls.from_libcloud(self, item)
                    continue

                subdir = subdirs[0]
                if subdir in dirs:
                    continue

                dirs.add(subdir)
                yield self.obj_cls(
                    self,
                    name=(path + SEP + subdir).lstrip(SEP),
                    obj_type=self.obj_cls.type_cls.SUBDIR,
                )

        objs = client.iterate_container_objects(self.native_container, path)
        objs = get_files_and_directories(objs)
        objs = islice(objs, limit)

        return list(objs)

    @wrap_libcloud_errors
    def get_object(self, path):
        """Get single object."""
        obj = self.native_container.get_object(path)
        return self.obj_cls.from_libcloud(self, obj)

    @classmethod
    def from_libcloud(cls, conn, container):
        """Create container from `libcloud.storage.base.Container`."""
        return cls(conn, container.name)


class ApacheLibcloudConnection(base.CloudConnection):
    """ApacheLibcloud connection wrapper."""

    #: Container child class.
    cont_cls = ApacheLibcloudContainer

    #: Exception translations.
    wrap_libcloud_errors = ApacheLibcloudExceptionWrapper()

    def __init__(self, provider, account, secret_key):
        """Initializer."""
        super(ApacheLibcloudConnection, self).__init__(account, secret_key)
        self.provider = provider

    @wrap_libcloud_errors
    @requires(libcloud, "libcloud")
    def _get_connection(self):
        """Return native connection object."""
        driver = libcloud.get_driver(libcloud.DriverType.STORAGE, self.provider.lower())

        return driver(self.account, self.secret_key)

    @wrap_libcloud_errors
    def _get_containers(self):
        """Return available containers."""
        return [
            self.cont_cls.from_libcloud(self, container)
            for container in self.native_conn.iterate_containers()
        ]

    @wrap_libcloud_errors
    def _get_container(self, path):
        """Return single container."""
        container = self.native_conn.get_container(path)
        return self.cont_cls.from_libcloud(self, container)
