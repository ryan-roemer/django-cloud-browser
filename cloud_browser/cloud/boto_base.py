"""Abstract boto-based datastore.

The boto_ library provides interfaces to both Amazon S3 and Google Storage
for Developers. This abstract base class gets most of the common work done.

.. note::
    **Installation**: Use of this module requires the open source boto_
    package.

.. _boto: http://code.google.com/p/boto/
"""
from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP, requires, dt_from_header

###############################################################################
# Constants / Conditional Imports
###############################################################################
try:
    import boto  # pylint: disable=F0401
except ImportError:
    boto = None  # pylint: disable=C0103


###############################################################################
# Classes
###############################################################################
class BotoExceptionWrapper(errors.CloudExceptionWrapper):
    """Boto :mod:`boto` exception translator."""
    error_cls = errors.CloudException

    @requires(boto, 'boto')
    def translate(self, exc):
        """Return whether or not to do translation."""
        from boto.exception import StorageResponseError

        if isinstance(exc, StorageResponseError):
            if exc.status == 404:
                return self.error_cls(unicode(exc))

        return None


class BotoKeyWrapper(errors.CloudExceptionWrapper):
    """Boto :mod:`boto` key exception translator."""
    error_cls = errors.NoObjectException


class BotoBucketWrapper(errors.CloudExceptionWrapper):
    """Boto :mod:`boto` bucket exception translator."""
    error_cls = errors.NoContainerException


class BotoObject(base.CloudObject):
    """Boto 'key' object wrapper."""
    #: Exception translations.
    wrap_boto_errors = BotoKeyWrapper()

    @classmethod
    def is_key(cls, result):
        """Return ``True`` if result is a key object."""
        raise NotImplementedError

    @classmethod
    def is_prefix(cls, result):
        """Return ``True`` if result is a prefix object."""
        raise NotImplementedError

    @wrap_boto_errors
    def _get_object(self):
        """Return native storage object."""
        return self.container.native_container.get_key(self.name)

    @wrap_boto_errors
    def _read(self):
        """Return contents of object."""
        return self.native_obj.read()

    @classmethod
    def from_result(cls, container, result):
        """Create from ambiguous result."""
        if result is None:
            raise errors.NoObjectException

        elif cls.is_prefix(result):
            return cls.from_prefix(container, result)

        elif cls.is_key(result):
            return cls.from_key(container, result)

        raise errors.CloudException("Unknown boto result type: %s" %
                                    type(result))

    @classmethod
    def from_prefix(cls, container, prefix):
        """Create from prefix object."""
        if prefix is None:
            raise errors.NoObjectException

        return cls(container,
                   name=prefix.name,
                   obj_type=cls.type_cls.SUBDIR)

    @classmethod
    def from_key(cls, container, key):
        """Create from key object."""
        if key is None:
            raise errors.NoObjectException

        # Get Key   (1123): Tue, 13 Apr 2010 14:02:48 GMT
        # List Keys (8601): 2010-04-13T14:02:48.000Z
        return cls(container,
                   name=key.name,
                   size=key.size,
                   content_type=key.content_type,
                   content_encoding=key.content_encoding,
                   last_modified=dt_from_header(key.last_modified),
                   obj_type=cls.type_cls.FILE)


class BotoContainer(base.CloudContainer):
    """Boto container wrapper."""
    #: Storage object child class.
    obj_cls = BotoObject

    #: Exception translations.
    wrap_boto_errors = BotoBucketWrapper()

    #: Maximum number of objects that can be listed or ``None``.
    #:
    #: :mod:`boto` transparently pages through objects, so there is no real
    #: limit to the number of object that can be displayed.  However, for
    #: practical reasons, we'll limit it to the same as Rackspace.
    max_list = 10000

    @wrap_boto_errors
    def _get_container(self):
        """Return native container object."""
        return self.conn.native_conn.get_bucket(self.name)

    @wrap_boto_errors
    def get_objects(self, path, marker=None,
                    limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get objects."""
        from itertools import islice

        path = path.rstrip(SEP) + SEP if path else path
        result_set = self.native_container.list(path, SEP, marker)

        # Get +1 results because marker and first item can match as we strip
        # the separator from results obscuring things. No real problem here
        # because boto masks any real request limits.
        results = list(islice(result_set, limit+1))
        if results:
            if marker and results[0].name.rstrip(SEP) == marker.rstrip(SEP):
                results = results[1:]
            else:
                results = results[:limit]

        return [self.obj_cls.from_result(self, r) for r in results]

    @wrap_boto_errors
    def get_object(self, path):
        """Get single object."""
        key = self.native_container.get_key(path)
        return self.obj_cls.from_key(self, key)

    @classmethod
    def from_bucket(cls, connection, bucket):
        """Create from bucket object."""
        if bucket is None:
            raise errors.NoContainerException

        # It appears that Amazon does not have a single-shot REST query to
        # determine the number of keys / overall byte size of a bucket.
        return cls(connection, bucket.name)


class BotoConnection(base.CloudConnection):
    """Boto connection wrapper."""
    #: Container child class.
    cont_cls = BotoContainer

    #: Exception translations.
    wrap_boto_errors = BotoBucketWrapper()

    def _get_connection(self):
        """Return native connection object."""
        raise NotImplementedError("Must create boto connection.")

    @wrap_boto_errors
    def _get_containers(self):
        """Return available containers."""
        buckets = self.native_conn.get_all_buckets()
        return [self.cont_cls.from_bucket(self, b) for b in buckets]

    @wrap_boto_errors
    def _get_container(self, path):
        """Return single container."""
        bucket = self.native_conn.get_bucket(path)
        return self.cont_cls.from_bucket(self, bucket)
