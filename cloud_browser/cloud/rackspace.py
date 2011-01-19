"""Rackspace cloud wrapper."""
from datetime import datetime

try:
    import cloudfiles  # pylint: disable=F0401
except ImportError:
    cloudfiles = None  # pylint: disable=C0103

from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP


# Current Rackspace maximum.
RS_MAX_GET_OBJS_LIMIT = 10000


class RackspaceExceptionWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        cloudfiles.errors.NoSuchContainer: errors.NoContainerException,
        cloudfiles.errors.NoSuchObject: errors.NoObjectException,
    }
wrap_rs_errors = RackspaceExceptionWrapper()  # pylint: disable=C0103


class RackspaceObject(base.CloudObject):
    """Cloud object wrapper."""

    @wrap_rs_errors
    def _get_object(self):
        """Return native storage object."""
        return self.container.native_container.get_object(self.name)

    @wrap_rs_errors
    def _read(self):
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
        return cls(container,
                   info_obj['subdir'],
                   obj_type=cls.type_cls.SUBDIR)

    @classmethod
    def from_file_info(cls, container, info_obj):
        """Create from regular info object."""
        # 2010-04-15T01:52:13.919070
        dt_str = info_obj['last_modified'].partition('.')[0]
        last_modified = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        return cls(container,
                   name=info_obj['name'],
                   size=info_obj['bytes'],
                   content_type=info_obj['content_type'],
                   last_modified=last_modified,
                   obj_type=cls.type_cls.FILE)

    @classmethod
    def from_obj(cls, container, file_obj):
        """Create from regular info object."""
        # Thu, 07 Jun 2007 18:57:07 GMT
        dt_str = file_obj.last_modified
        last_modified = datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S GMT")
        return cls(container,
                   name=file_obj.name,
                   size=file_obj.size,
                   content_type=file_obj.content_type,
                   last_modified=last_modified,
                   obj_type=cls.type_cls.FILE)


class RackspaceContainer(base.CloudContainer):
    """Rackspace container wrapper."""
    obj_cls = RackspaceObject

    @wrap_rs_errors
    def _get_container(self):
        """Return native container object."""
        return self.conn.native_conn.get_container(self.name)

    @wrap_rs_errors
    def get_objects(self, path, marker=None,
                    limit=base.DEFAULT_GET_OBJS_LIMIT):
        """Get objects."""
        # Require 1 less than RS max. to allow for "next" count.
        if limit >= RS_MAX_GET_OBJS_LIMIT - 1:
            raise errors.CloudException("Object limit must be less than %s" %
                                        (RS_MAX_GET_OBJS_LIMIT - 1))

        path = path + SEP if path else ''
        object_infos = self.native_container.list_objects_info(
            limit=limit, delimiter=SEP, prefix=path, marker=marker)

        return [self.obj_cls.from_info(self, x) for x in object_infos]

    @wrap_rs_errors
    def get_object(self, path):
        """Get single object."""
        obj = self.native_container.get_object(path)
        return self.obj_cls.from_obj(self, obj)


class RackspaceConnection(base.CloudConnection):
    """Rackspace connection wrapper."""
    cont_cls = RackspaceContainer

    def __init__(self, account, secret_key, rs_servicenet=False):
        """Initializer."""
        super(RackspaceConnection, self).__init__(account, secret_key)
        self.rs_servicenet = rs_servicenet

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

        return cloudfiles.get_connection(**kwargs)  # pylint: disable=W0142

    @wrap_rs_errors
    def _get_containers(self):
        """Return available containers."""
        infos = self.native_conn.list_containers_info()
        return [self.cont_cls(self, i['name'], i['count'], i['bytes'])
                for i in infos]

    @wrap_rs_errors
    def _get_container(self, path):
        """Return single container."""
        cont = self.native_conn.get_container(path)
        return self.cont_cls(self,
                             cont.name,
                             cont.object_count,
                             cont.size_used)
