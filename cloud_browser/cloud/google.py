"""Google Storage for Developers datastore.

`Google Storage for Developers`_ (GS) is cosmetically an implementation of the
S3 interface by Google.

.. note::
    **Installation**: Use of this module requires the open source boto_
    package. Not sure exactly which version installed GS support, but we'll
    validate the version if it becomes an issue.

.. _`Google Storage for Developers`: http://code.google.com/apis/storage/
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
class GsObject(base.BotoObject):
    """Google Storage 'key' object wrapper."""

    @classmethod
    @requires(boto, 'boto')
    def is_key(cls, result):
        """Return ``True`` if result is a key object."""
        from boto.gs.key import Key

        return isinstance(result, Key)

    @classmethod
    @requires(boto, 'boto')
    def is_prefix(cls, result):
        """Return ``True`` if result is a prefix object.

        .. note::
            Boto uses the S3 Prefix object for GS prefixes.
        """
        from boto.s3.prefix import Prefix

        return isinstance(result, Prefix)


class GsContainer(base.BotoContainer):
    """Google Storage container wrapper."""
    #: Storage object child class.
    obj_cls = GsObject


class GsConnection(base.BotoConnection):
    """Google Storage connection wrapper."""
    #: Container child class.
    cont_cls = GsContainer

    @base.BotoConnection.wrap_boto_errors
    @requires(boto, 'boto')
    def _get_connection(self):
        """Return native connection object."""
        return boto.connect_gs(self.account, self.secret_key)
