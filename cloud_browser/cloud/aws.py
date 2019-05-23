"""Amazon Simple Storage Service (S3) datastore.

.. note::
    **Installation**: Use of this module requires the open source boto_
    package.

.. _boto: http://code.google.com/p/boto/
"""
from cloud_browser.cloud import boto_base as base
from cloud_browser.common import requires

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
class AwsObject(base.BotoObject):
    """AWS 'key' object wrapper."""

    @classmethod
    @requires(boto, "boto")
    def is_key(cls, result):
        """Return ``True`` if result is a key object."""
        from boto.s3.key import Key

        return isinstance(result, Key)

    @classmethod
    @requires(boto, "boto")
    def is_prefix(cls, result):
        """Return ``True`` if result is a prefix object."""
        from boto.s3.prefix import Prefix

        return isinstance(result, Prefix)


class AwsContainer(base.BotoContainer):
    """AWS container wrapper."""

    #: Storage object child class.
    obj_cls = AwsObject


class AwsConnection(base.BotoConnection):
    """AWS connection wrapper."""

    #: Container child class.
    cont_cls = AwsContainer

    @base.BotoConnection.wrap_boto_errors
    @requires(boto, "boto")
    def _get_connection(self):
        """Return native connection object."""
        return boto.connect_s3(self.account, self.secret_key)
