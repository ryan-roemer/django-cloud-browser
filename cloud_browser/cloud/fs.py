"""File-system mock cloud wrapper."""
import os
import re

from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP


class FilesystemObject(base.CloudObject):
    """Filesystem object wrapper."""

    def _get_object(self):
        """Return native storage object."""
        return "TODO"

    def _read(self):
        """Return contents of object."""
        return "TODO"


class FilesystemContainer(base.CloudContainer):
    """Filesystem container wrapper."""
    obj_cls = FilesystemObject

    def _get_container(self):
        """Return native container object."""
        return "TODO"

    # TODO: set limit to DEFAULT_LIMIT
    def get_objects(self, path, marker=None, limit=20):
        """Get objects."""
        return ["TODO"]

    def get_object(self, path):
        """Get single object."""
        return "TODO"

    @property
    def base_path(self):
        """Base absolute path of container."""
        return os.path.join(self.conn.abs_root, self.name)

    @classmethod
    def from_path(cls, conn, path):
        """Create container from path."""
        path = path.strip(SEP)
        full_path = os.path.join(conn.abs_root, path)
        return cls(conn, path, 0, os.path.getsize(full_path))


class FilesystemConnection(base.CloudConnection):
    """Filesystem connection wrapper."""
    cont_cls = FilesystemContainer
    cont_filter = re.compile("^[^.]+")

    def __init__(self, root):
        """Initializer."""
        super(FilesystemConnection, self).__init__(None, None)
        self.root = root
        self.abs_root = os.path.abspath(root)

    def _get_connection(self):
        """Return native connection object."""
        return object()

    def get_containers(self):
        """Return available containers."""
        def _include(dir_name):
            """Filter function."""
            return self.cont_filter.match(dir_name) and os.path.isdir(dir_name)

        return [self.cont_cls.from_path(self, d)
                for d in os.listdir(self.abs_root) if _include(d)]

    def get_container(self, path):
        """Return single container."""
        path = path.strip(SEP)
        if SEP in path:
            raise errors.InvalidNameException(
                "Path contains %s - %s" % (SEP, path))
        return self.cont_cls.from_path(self, path)
