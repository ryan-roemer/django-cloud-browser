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
from cloud_browser.app_settings import settings
from cloud_browser.cloud import boto_base as base
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
class GsObject(base.BotoObject):
    """Google Storage 'key' object wrapper."""

    _gs_folder_suffix = "_$folder$"

    @classmethod
    def _is_gs_folder(cls, result):
        """Return ``True`` if GS standalone folder object.

        GS will create a 0 byte ``<FOLDER NAME>_$folder$`` key as a
        pseudo-directory place holder if there are no files present.
        """
        return (
            cls.is_key(result)
            and result.size == 0
            and result.name.endswith(cls._gs_folder_suffix)
        )

    @classmethod
    @requires(boto, "boto")
    def is_key(cls, result):
        """Return ``True`` if result is a key object."""
        from boto.gs.key import Key

        return isinstance(result, Key)

    @classmethod
    @requires(boto, "boto")
    def is_prefix(cls, result):
        """Return ``True`` if result is a prefix object.

        .. note::
            Boto uses the S3 Prefix object for GS prefixes.
        """
        from boto.s3.prefix import Prefix

        return isinstance(result, Prefix) or cls._is_gs_folder(result)

    @classmethod
    def from_prefix(cls, container, prefix):
        """Create from prefix object."""
        if cls._is_gs_folder(prefix):
            name, suffix, extra = prefix.name.partition(cls._gs_folder_suffix)
            if (suffix, extra) == (cls._gs_folder_suffix, ""):
                # Patch GS specific folder to remove suffix.
                prefix.name = name

        return super(GsObject, cls).from_prefix(container, prefix)


class GsContainer(base.BotoContainer):
    """Google Storage container wrapper."""

    #: Storage object child class.
    obj_cls = GsObject

    def get_objects(
        self, path, marker=None, limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT
    ):
        """Get objects.

        Certain upload clients may add a 0-byte object (e.g., ``FOLDER`` object
        for path ``path/to/FOLDER`` - ``path/to/FOLDER/FOLDER``). We add an
        extra +1 limit query and ignore any such file objects.
        """
        # Get basename of implied folder.
        folder = path.split(SEP)[-1]

        # Query extra objects, then strip 0-byte dummy object if present.
        objs = super(GsContainer, self).get_objects(path, marker, limit + 1)
        objs = [o for o in objs if not (o.size == 0 and o.name == folder)]

        return objs[:limit]


class GsConnection(base.BotoConnection):
    """Google Storage connection wrapper."""

    #: Container child class.
    cont_cls = GsContainer

    @base.BotoConnection.wrap_boto_errors
    @requires(boto, "boto")
    def _get_connection(self):
        """Return native connection object."""
        return boto.connect_gs(self.account, self.secret_key)
