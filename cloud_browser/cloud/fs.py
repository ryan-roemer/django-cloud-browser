"""File-system datastore."""
from __future__ import with_statement

import os
import re

from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP


###############################################################################
# Helpers / Constants
###############################################################################
NO_DOT_RE = re.compile("^[^.]+")


def not_dot(path):
    """Check if non-dot."""
    return NO_DOT_RE.match(os.path.basename(path))


def is_dir(path):
    """Check if non-dot and directory."""
    return not_dot(path) and os.path.isdir(path)


###############################################################################
# Classes
###############################################################################
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


class FilesystemObject(base.CloudObject):
    """Filesystem object wrapper."""

    def _get_object(self):
        """Return native storage object."""
        return object()

    def _read(self):
        """Return contents of object."""
        with open(self.base_path, 'rb') as file_obj:
            return file_obj.read()

    @property
    def base_path(self):
        """Base absolute path of container."""
        return os.path.join(self.container.base_path, self.name)

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
    #: Storage object child class.
    obj_cls = FilesystemObject

    def _get_container(self):
        """Return native container object."""
        return object()

    @wrap_fs_obj_errors
    def get_objects(self, path, marker=None,
                    limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get objects."""
        def _filter(name):
            """Filter."""
            return (not_dot(name) and
                    (marker is None or
                     os.path.join(path, name).strip(SEP) > marker.strip(SEP)))

        search_path = os.path.join(self.base_path, path)
        objs = [self.obj_cls.from_path(self, os.path.join(path, o))
                for o in os.listdir(search_path) if _filter(o)]
        objs = sorted(objs, key=lambda x: x.base_path)
        return objs[:limit]

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
    #: Container child class.
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
    def _get_containers(self):
        """Return available containers."""
        full_fn = lambda p: os.path.join(self.abs_root, p)
        return [self.cont_cls.from_path(self, d)
                for d in os.listdir(self.abs_root) if is_dir(full_fn(d))]

    @wrap_fs_cont_errors
    def _get_container(self, path):
        """Return single container."""
        path = path.strip(SEP)
        if SEP in path:
            raise errors.InvalidNameException(
                "Path contains %s - %s" % (SEP, path))
        return self.cont_cls.from_path(self, path)
