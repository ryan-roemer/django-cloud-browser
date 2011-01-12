"""File-system mock cloud wrapper."""
import os
import re

from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP


NO_DOT_RE = re.compile("^[^.]+")


def not_dot(path):
    """Check if non-dot."""
    return NO_DOT_RE.match(os.path.basename(path))


def is_dir(path):
    """Check if non-dot and directory."""
    return not_dot(path) and os.path.isdir(path)


class FilesystemContainerWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        OSError: errors.NoContainerException,
    }
wrap_fs_cont_errors = FilesystemContainerWrapper()  # pylint: disable=C0103


class FilesystemObjectWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        OSError: errors.NoObjectException,
    }
wrap_fs_obj_errors = FilesystemObjectWrapper()  # pylint: disable=C0103


# TODO: Handle empty directory (with non non-dot files).
class FilesystemObject(base.CloudObject):
    """Filesystem object wrapper."""

    def _get_object(self):
        """Return native storage object."""
        return object()

    def _read(self):
        """Return contents of object."""
        return "TODO"

    @classmethod
    def from_path(cls, container, path):
        """Create object from path."""
        from datetime import datetime

        path = path.strip(SEP)
        full_path = os.path.join(container.base_path, path)
        last_modified = datetime.fromtimestamp(os.path.getmtime(full_path))
        obj_type = cls.type_cls.SUBDIR if is_dir(full_path)\
            else cls.type_cls.FILE

        return cls(container,
                   name=path,
                   size=os.path.getsize(full_path),
                   content_type=None,
                   last_modified=last_modified,
                   obj_type=obj_type)


class FilesystemContainer(base.CloudContainer):
    """Filesystem container wrapper."""
    obj_cls = FilesystemObject

    def _get_container(self):
        """Return native container object."""
        return object()

    # TODO: get_objects - set limit to DEFAULT_LIMIT
    # TODO: get_objects - Actually use marker!
    @wrap_fs_obj_errors
    def get_objects(self, path, marker=None, limit=20):
        """Get objects."""
        search_path = os.path.join(self.base_path, path)
        return [self.obj_cls.from_path(self, os.path.join(path, d))
                for d in os.listdir(search_path) if not_dot(d)][:limit]

    @wrap_fs_obj_errors
    def get_object(self, path):
        """Get single object."""
        return self.obj_cls.from_path(self, path)

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

    def __init__(self, root):
        """Initializer."""
        super(FilesystemConnection, self).__init__(None, None)
        self.root = root
        self.abs_root = os.path.abspath(root)

    def _get_connection(self):
        """Return native connection object."""
        return object()

    @wrap_fs_cont_errors
    def get_containers(self):
        """Return available containers."""
        full_fn = lambda p: os.path.join(self.abs_root, p)
        return [self.cont_cls.from_path(self, d)
                for d in os.listdir(self.abs_root) if is_dir(full_fn(d))]

    @wrap_fs_cont_errors
    def get_container(self, path):
        """Return single container."""
        path = path.strip(SEP)
        if SEP in path:
            raise errors.InvalidNameException(
                "Path contains %s - %s" % (SEP, path))
        return self.cont_cls.from_path(self, path)
