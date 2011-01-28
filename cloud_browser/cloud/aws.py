"""Amazon Web Services (S3) cloud wrapper.

.. note::
    **Installation**: Use of this module requires the open source :mod:`boto`
    package.
"""
from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP, requires

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
class AwsExceptionWrapper(errors.CloudExceptionWrapper):
    """Rackspace :mod:`boto` exception translator."""

    @classmethod
    @requires(boto, 'boto')
    def lazy_translations(cls):
        """Lazy translations."""
        return  {}  # TODO: Insert actual boto translations.


class AwsObject(base.CloudObject):
    """AWS 'key' object wrapper."""
    #: Exception translations.
    wrap_aws_errors = AwsExceptionWrapper()

    @wrap_aws_errors
    def _get_object(self):
        """Return native storage object."""
        return self.container.native_container.get_key(self.name)

    @wrap_aws_errors
    def _read(self):
        """Return contents of object."""
        return self.native_obj.read()

    @classmethod
    def from_result(cls, container, result):
        """Create from ambiguous result."""
        from boto.s3.key import Key
        from boto.s3.prefix import Prefix

        if isinstance(result, Key):
            return cls.from_key(container, result)

        elif isinstance(result, Prefix):
            return cls.from_prefix(container, result)

        raise errors.CloudException("Unknown boto result type: %s" %
                                    type(result))

    @classmethod
    def from_prefix(cls, container, prefix):
        """Create from prefix object."""
        return cls(container,
                   name=prefix.name,
                   obj_type=cls.type_cls.SUBDIR)

    @classmethod
    def from_key(cls, container, key):
        """Create from key object."""
        # TODO: Convert last_modified to ``datetime``.
        return cls(container,
                   name=key.name,
                   size=key.size,
                   content_type=key.content_type,
                   content_encoding=key.content_encoding,
                   last_modified=key.last_modified,
                   obj_type=cls.type_cls.FILE)


class AwsContainer(base.CloudContainer):
    """Rackspace container wrapper."""
    #: Storage object child class.
    obj_cls = AwsObject

    #: Exception translations.
    wrap_aws_errors = AwsExceptionWrapper()

    #: Maximum number of objects that can be listed or ``None``.
    max_list = 1000  # TODO: Figure out this limit.

    @wrap_aws_errors
    def _get_container(self):
        """Return native container object."""
        return self.conn.native_conn.get_bucket(self.name)

    @wrap_aws_errors
    def get_objects(self, path, marker=None,
                    limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get objects."""
        from itertools import islice

        # TODO: (BUG) marker is "off by one" for next set.
        path = path.rstrip(SEP) + SEP if path else path
        result_set = self.native_container.list(path, SEP, marker)
        results = islice(result_set, limit)
        return [self.obj_cls.from_result(self, r) for r in results]

    @wrap_aws_errors
    def get_object(self, path):
        """Get single object."""
        key = self.native_container.get_key(path)
        return self.obj_cls.from_key(self, key)

    @classmethod
    def from_bucket(cls, connection, bucket):
        """Create from bucket object."""
        # TODO: Find bucket count and size.
        return cls(connection, bucket.name)


class AwsConnection(base.CloudConnection):
    """AWS connection wrapper."""
    #: Container child class.
    cont_cls = AwsContainer

    #: Exception translations.
    wrap_aws_errors = AwsExceptionWrapper()

    @wrap_aws_errors
    @requires(boto, 'boto')
    def _get_connection(self):
        """Return native connection object."""
        return boto.connect_s3(self.account, self.secret_key)

    @wrap_aws_errors
    def _get_containers(self):
        """Return available containers."""
        buckets = self.native_conn.get_all_buckets()
        return [self.cont_cls.from_bucket(self, b) for b in buckets]

    @wrap_aws_errors
    def _get_container(self, path):
        """Return single container."""
        bucket = self.native_conn.get_bucket(path)
        return self.cont_cls.from_bucket(self, bucket)
