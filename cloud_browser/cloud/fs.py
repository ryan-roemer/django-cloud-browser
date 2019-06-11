"""File-system datastore."""
from __future__ import with_statement

import os
import re

from cloud_browser.app_settings import settings
from cloud_browser.cloud import base, errors
from cloud_browser.common import SEP

###############################################################################
# Helpers / Constants
###############################################################################
NO_DOT_RE = re.compile("^[^.]+")


def path_to_os(path):
    return path.replace(SEP, os.path.sep)


def os_to_path(path):
    return path.replace(os.path.sep, SEP)


def not_dot(path):
    return NO_DOT_RE.match(os.path.basename(path_to_os(path)))


def is_dir(path):
    return not_dot(path) and os.path.isdir(path_to_os(path))


def listdir(path):
    return [os_to_path(result) for result in os.listdir(path_to_os(path))]


def getmtime(path):
    return os.path.getmtime(path_to_os(path))


def getsize(path):
    return os.path.getsize(path_to_os(path))


def abspath(path):
    return os.path.abspath(path_to_os(path))


###############################################################################
# Classes
###############################################################################
class FilesystemContainerWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""

    translations = {OSError: errors.NoContainerException}


class FilesystemObjectWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""

    translations = {OSError: errors.NoObjectException}


wrap_fs_cont_errors = FilesystemContainerWrapper()  # pylint: disable=C0103
wrap_fs_obj_errors = FilesystemObjectWrapper()  # pylint: disable=C0103


class FilesystemObject(base.CloudObject):
    """Filesystem object wrapper."""

    def _get_object(self):
        """Return native storage object."""
        return object()

    def _read(self):
        """Return contents of object."""
        with open(self.base_path, "rb") as file_obj:
            return file_obj.read()

    @property
    def base_path(self):
        """Base absolute path of container."""
        return SEP.join((self.container.base_path, self.name))

    @classmethod
    def from_path(cls, container, path):
        """Create object from path."""
        from datetime import datetime

        path = path.strip(SEP)
        full_path = SEP.join((container.base_path, path))
        last_modified = datetime.fromtimestamp(getmtime(full_path))
        obj_type = cls.type_cls.SUBDIR if is_dir(full_path) else cls.type_cls.FILE

        return cls(
            container,
            name=path,
            size=getsize(full_path),
            content_type=None,
            last_modified=last_modified,
            obj_type=obj_type,
        )


class FilesystemContainer(base.CloudContainer):
    """Filesystem container wrapper."""

    #: Storage object child class.
    obj_cls = FilesystemObject

    def _get_container(self):
        """Return native container object."""
        return object()

    @wrap_fs_obj_errors
    def get_objects(
        self, path, marker=None, limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT
    ):
        """Get objects."""

        def _filter(name):
            """Filter."""
            return not_dot(name) and (
                marker is None or SEP.join((path, name)).strip(SEP) > marker.strip(SEP)
            )

        search_path = SEP.join((self.base_path, path))
        objs = [
            self.obj_cls.from_path(self, SEP.join((path, o)))
            for o in listdir(search_path)
            if _filter(o)
        ]
        objs = sorted(objs, key=lambda x: x.base_path)
        return objs[:limit]

    @wrap_fs_obj_errors
    def get_object(self, path):
        """Get single object."""
        return self.obj_cls.from_path(self, path)

    @property
    def base_path(self):
        """Base absolute path of container."""
        return SEP.join((self.conn.abs_root, self.name))

    @classmethod
    def from_path(cls, conn, path):
        """Create container from path."""
        path = path.strip(SEP)
        full_path = SEP.join((conn.abs_root, path))
        return cls(conn, path, 0, getsize(full_path))


class FilesystemConnection(base.CloudConnection):
    """Filesystem connection wrapper."""

    #: Container child class.
    cont_cls = FilesystemContainer

    def __init__(self, root):
        """Initializer."""
        super(FilesystemConnection, self).__init__(None, None)
        self.root = root
        self.abs_root = abspath(root)

    def _get_connection(self):
        """Return native connection object."""
        return object()

    @wrap_fs_cont_errors
    def _get_containers(self):
        """Return available containers."""

        def full_fn(path):
            return SEP.join((self.abs_root, path))

        return [
            self.cont_cls.from_path(self, d)
            for d in listdir(self.abs_root)
            if is_dir(full_fn(d))
        ]

    @wrap_fs_cont_errors
    def _get_container(self, path):
        """Return single container."""
        path = path.strip(SEP)
        if SEP in path:
            raise errors.InvalidNameException("Path contains %s - %s" % (SEP, path))
        return self.cont_cls.from_path(self, path)
