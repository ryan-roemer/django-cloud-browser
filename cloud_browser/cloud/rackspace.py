"""Rackspace Cloud Files datastore.

.. note::
    **Installation**: Use of this module requires the Rackspace
    cloudfiles_ package, and at least version 1.7.4 (which introduced the
    ``delimiter`` container query support).

.. _cloudfiles: https://github.com/rackspace/python-cloudfiles
"""
from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP, check_version, requires, dt_from_header

###############################################################################
# Constants / Conditional Imports
###############################################################################
# 1.7.4 introduced the ``path`` parameter for ``list_objects_info``.
RS_MIN_CLOUDFILES_VERSION = (1, 7, 4)

# Current Rackspace maximum number of objects/containers for listing.
RS_MAX_LIST_OBJECTS_LIMIT = 10000
RS_MAX_LIST_CONTAINERS_LIMIT = 10000

try:
    import cloudfiles  # pylint: disable=F0401
    check_version(cloudfiles, RS_MIN_CLOUDFILES_VERSION)
except ImportError:
    cloudfiles = None  # pylint: disable=C0103


###############################################################################
# Classes
###############################################################################
class RackspaceExceptionWrapper(errors.CloudExceptionWrapper):
    """Rackspace :mod:`cloudfiles` exception translator."""

    @classmethod
    @requires(cloudfiles, 'cloudfiles')
    def lazy_translations(cls):
        """Lazy translations."""
        return  {
            cloudfiles.errors.NoSuchContainer: errors.NoContainerException,
            cloudfiles.errors.NoSuchObject: errors.NoObjectException,
        }


class RackspaceObject(base.CloudObject):
    """Cloud object wrapper."""
    #: Exception translations.
    wrap_rs_errors = RackspaceExceptionWrapper()

    #: Subdirectory content types.
    #: Rackspace has "special" content types that should be interpreted as
    #: pseudo-directory delimiters from "old style" hierarchy detection.
    subdir_types = set((
        "application/directory",
        "application/folder",
    ))

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
    def choose_type(cls, content_type):
        """Choose object type from content type."""
        return cls.type_cls.SUBDIR if content_type in cls.subdir_types \
            else cls.type_cls.FILE

    @classmethod
    def from_file_info(cls, container, info_obj):
        """Create from regular info object."""
        # RFC 8601: 2010-04-15T01:52:13.919070
        return cls(container,
                   name=info_obj['name'],
                   size=info_obj['bytes'],
                   content_type=info_obj['content_type'],
                   last_modified=dt_from_header(info_obj['last_modified']),
                   obj_type=cls.choose_type(info_obj['content_type']))

    @classmethod
    def from_obj(cls, container, file_obj):
        """Create from regular info object."""
        # RFC 1123: Thu, 07 Jun 2007 18:57:07 GMT
        return cls(container,
                   name=file_obj.name,
                   size=file_obj.size,
                   content_type=file_obj.content_type,
                   last_modified=dt_from_header(file_obj.last_modified),
                   obj_type=cls.choose_type(file_obj.content_type))


class RackspaceContainer(base.CloudContainer):
    """Rackspace container wrapper."""
    #: Storage object child class.
    obj_cls = RackspaceObject

    #: Exception translations.
    wrap_rs_errors = RackspaceExceptionWrapper()

    #: Maximum number of objects that can be listed or ``None``.
    #:
    #: Enforced Rackspace maximums. We need a lower max. to be enforced on
    #: the input end because under the hood, we can try subsequent larger
    #: queries if we have marker or psuedo/dummy directory clashes.
    #:
    #: Specifically, we need to add one to the query to detect a
    #: pseudo-directory matching the marker, and double the limit for a
    #: follow-on query if we have both dummy and pseudo-directory objects
    #: in results.
    max_list = (RS_MAX_LIST_OBJECTS_LIMIT - 1) / 2

    @wrap_rs_errors
    def _get_container(self):
        """Return native container object."""
        return self.conn.native_conn.get_container(self.name)

    @wrap_rs_errors
    def get_objects(self, path, marker=None,
                    limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get objects.

        **Pseudo-directory Notes**: Rackspace has two approaches to pseudo-
        directories within the (really) flat storage object namespace:

          1. Dummy directory storage objects. These are real storage objects
             of type "application/directory" and must be manually uploaded
             by the client.
          2. Implied subdirectories using the `path` API query parameter.

        Both serve the same purpose, but the latter is much preferred because
        there is no independent maintenance of extra dummy objects, and the
        `path` approach is always correct (for the existing storage objects).

        This package uses the latter `path` approach, but gets into an
        ambiguous situation where there is both a dummy directory storage
        object and an implied subdirectory. To remedy this situation, we only
        show information for the dummy directory object in results if present,
        and ignore the implied subdirectory. But, under the hood this means
        that our `limit` parameter may end up with less than the desired
        number of objects. So, we use the heuristic that if we **do** have
        "application/directory" objects, we end up doing an extra query of
        double the limit size to ensure we can get up to the limit amount
        of objects. This double query approach is inefficient, but as
        using dummy objects should now be deprecated, the second query should
        only rarely occur.

        """
        object_infos, full_query = self._get_object_infos(path, marker, limit)
        if full_query and len(object_infos) < limit:
            # The underlying query returned a full result set, but we
            # truncated it to under limit. Re-run at twice the limit and then
            # slice back.
            object_infos, _ = self._get_object_infos(path, marker, 2*limit)
            object_infos = object_infos[:limit]

        return [self.obj_cls.from_info(self, x) for x in object_infos]

    @wrap_rs_errors
    def _get_object_infos(self, path, marker=None,
                          limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get raw object infos (single-shot)."""
        # Adjust limit to +1 to handle marker object as first result.
        # We can get in to this situation for a marker of "foo", that will
        # still return a 'subdir' object of "foo/" because of the extra
        # slash.
        orig_limit = limit
        limit += 1

        # Enforce maximum object size.
        if limit > RS_MAX_LIST_OBJECTS_LIMIT:
            raise errors.CloudException("Object limit must be less than %s" %
                                        RS_MAX_LIST_OBJECTS_LIMIT)

        def _collapse(infos):
            """Remove duplicate dummy / implied objects."""
            name = None
            for info in infos:
                name = info.get('name', name)
                subdir = info.get('subdir', '').strip(SEP)
                if not name or subdir != name:
                    yield info

        path = path + SEP if path else ''
        object_infos = self.native_container.list_objects_info(
            limit=limit, delimiter=SEP, prefix=path, marker=marker)

        full_query = len(object_infos) == limit
        if object_infos:
            # Check first object for marker match and truncate if so.
            if (marker and
                    object_infos[0].get('subdir', '').strip(SEP) == marker):
                object_infos = object_infos[1:]

            # Collapse subdirs and dummy objects.
            object_infos = list(_collapse(object_infos))

            # Adjust to original limit.
            if len(object_infos) > orig_limit:
                object_infos = object_infos[:orig_limit]

        return object_infos, full_query

    @wrap_rs_errors
    def get_object(self, path):
        """Get single object."""
        obj = self.native_container.get_object(path)
        return self.obj_cls.from_obj(self, obj)


class RackspaceConnection(base.CloudConnection):
    """Rackspace connection wrapper."""
    #: Container child class.
    cont_cls = RackspaceContainer

    #: Exception translations.
    wrap_rs_errors = RackspaceExceptionWrapper()

    #: Maximum number of containers that can be listed or ``None``.
    max_list = RS_MAX_LIST_CONTAINERS_LIMIT

    def __init__(self, account, secret_key, servicenet=False, authurl=None):
        """Initializer."""
        super(RackspaceConnection, self).__init__(account, secret_key)
        self.servicenet = servicenet
        self.authurl = authurl

    @wrap_rs_errors
    @requires(cloudfiles, 'cloudfiles')
    def _get_connection(self):
        """Return native connection object."""
        kwargs = {
            'username': self.account,
            'api_key': self.secret_key,
        }

        # Only add kwarg for servicenet if True because user could set
        # environment variable 'RACKSPACE_SERVICENET' separately.
        if self.servicenet:
            kwargs['servicenet'] = True

        if self.authurl:
            kwargs['authurl'] = self.authurl

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
