"""Application-specific settings."""
import os

from django.conf import settings as _settings
from django.core.exceptions import ImproperlyConfigured


###############################################################################
# Single settings.
###############################################################################
class Setting(object):
    """Settings option helper class."""

    def __init__(self, **kwargs):
        """Initializer.

        :kwarg default: Override default for getting.
        :type  default: ``object``
        :kwarg from_env: Allow variable from evironment.
        :type  from_env: ``bool``
        :kwarg valid_set: Set of valid values for setting.
        :type  valid_set: ``set``
        """
        self.from_env = kwargs.get("from_env", False)
        self.default = kwargs.get("default", None)
        self.valid_set = kwargs.get("valid_set", None)

    def validate(self, name, value):
        """Validate and return a value."""

        if self.valid_set and value not in self.valid_set:
            raise ImproperlyConfigured(
                '%s: "%s" is not a valid setting (choose between %s).'
                % (name, value, ", ".join('"%s"' % x for x in self.valid_set))
            )

        return value

    def env_clean(self, value):  # pylint: disable=R0201
        """Clean / convert environment variable to proper type."""
        return value

    def get(self, name, default=None):
        """Get value."""
        default = default if default is not None else self.default
        try:
            value = getattr(_settings, name)
        except AttributeError:
            value = os.environ.get(name, default) if self.from_env else default
            # Convert env variable.
            if value != default:
                value = self.env_clean(value)

        return self.validate(name, value)


class BoolSetting(Setting):
    """Boolean setting.."""

    def env_clean(self, value):
        """Clean / convert environment variable to proper type."""
        return self.parse_bool(value)

    @classmethod
    def parse_bool(cls, value, default=None):
        """Convert ``string`` or ``bool`` to ``bool``."""
        if value is None:
            return default

        elif isinstance(value, bool):
            return value

        elif isinstance(value, str):
            if value == "True":
                return True
            elif value == "False":
                return False

        raise Exception("Value %s is not boolean." % value)


###############################################################################
# Settings wrapper.
###############################################################################
class Settings(object):
    """Cloud Browser application settings.

    This class wraps the "real" Django settings object, so can be used instead.
    The additional cloud browser settings are as follows:

    .. note::
      **Environment Variables**: Certain credential settings can come from OS
      environment variables instead of from a settings file value to open up
      more options for secrets management. Values that can be set in the
      environment are designated with an "(*Env*)" notation.

      Setting a value this way could be done, e.g.::

          $ export CLOUD_BROWSER_AWS_ACCOUNT="my_account"
          $ export CLOUD_BROWSER_AWS_SECRET_KEY="my_secret"
          $ # ... start django application with environment variables.

    **Datastore Settings**:

    * ``CLOUD_BROWSER_DATASTORE``: Choice of datastore (see values below).

    **Apache Libcloud**: Configure Apache Libcloud as backing datastore.

    * ``CLOUD_BROWSER_DATASTORE = "ApacheLibcloud"``
    * ``CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER``: Provider name. (*Env*)
    * ``CLOUD_BROWSER_APACHE_LIBCLOUD_ACCOUNT``: Account name. (*Env*)
    * ``CLOUD_BROWSER_APACHE_LIBCLOUD_SECRET_KEY``: Account secret. (*Env*)

    **Amazon Web Services**: Configure AWS S3 as backing datastore.

    * ``CLOUD_BROWSER_DATASTORE = "AWS"``
    * ``CLOUD_BROWSER_AWS_ACCOUNT``: Account name. (*Env*)
    * ``CLOUD_BROWSER_AWS_SECRET_KEY``: Account API secret key. (*Env*)

    **Google Storage for Developers**: Configure Google Storage as backing
    datastore.

    * ``CLOUD_BROWSER_DATASTORE = "Google"``
    * ``CLOUD_BROWSER_GS_ACCOUNT``: Account name. (*Env*)
    * ``CLOUD_BROWSER_GS_SECRET_KEY``: Account API secret key. (*Env*)

    **Rackspace**: Configure Rackspace Cloud Files as backing datastore.

    * ``CLOUD_BROWSER_DATASTORE = "Rackspace"``
    * ``CLOUD_BROWSER_RACKSPACE_ACCOUNT``: Account name. (*Env*)
    * ``CLOUD_BROWSER_RACKSPACE_SECRET_KEY``: Account API secret key. (*Env*)
    * ``CLOUD_BROWSER_RACKSPACE_SERVICENET``: Boolean designating whether or
      not to use Rackspace's servicenet (i.e., the private interface on a
      Cloud Server). (*Env*)
    * ``CLOUD_BROWSER_RACKSPACE_AUTHURL``: Alternative authorization server,
      for use, e.g., with `OpenStack <http://www.openstack.org/>`_ instead of
      Rackspace. (*Env*)

    **Filesystem**: Configure simple filesystem mock datastore.

    * ``CLOUD_BROWSER_DATASTORE = "Filesystem"``
    * ``CLOUD_BROWSER_FILESYSTEM_ROOT``: Filesystem root to serve from.

    **View Permissions**: A standard Django view decorator object can be
    specified, which is wrapped for all browsing / viewing view -- for example,
    to limit views to logged in members, use ``login_required`` and for staff
    only, use ``staff_member_required``. Note that either a real decorator
    function or a fully-qualifid string path are acceptable, so you can use,
    e.g., "django.contrib.admin.views.decorators.staff_member_required" instead
    which might help with certain settings.py import-order-related issues.

    * ``CLOUD_BROWSER_VIEW_DECORATOR``: View decorator or fully-qualified
      string path.

    **Container Permissions**: Cloud browser allows a very rudimentary form
    of access control at the container level with white and black lists.
    If the white list is set, only container names in the white list are
    allowed. If the white list is unset, then any container name *not* in
    the black list is permitted. All name matching is exact (no regular
    expressions, etc.).

    * ``CLOUD_BROWSER_CONTAINER_WHITELIST``: White list of names. (Iterable)
    * ``CLOUD_BROWSER_CONTAINER_BLACKLIST``: Black list of names. (Iterable)

    **General**: Other settings.

    * ``CLOUD_BROWSER_DEFAULT_LIST_LIMIT``: Default number of objects to
      diplay per browser page.

    * ``CLOUD_BROWSER_OBJECT_REDIRECT_URL``: Custom URL to which to redirect
      when clicking on an object (defaults to showing object contents).

    * ``CLOUD_BROWSER_STATIC_MEDIA_DIR``: If this applications static media
      (found in ``app_media``) is served up under the ``settings.MEDIA_ROOT``,
      then set a relative path from the root, and the static media will be used
      instead of a Django-based static view fallback.
    """

    #: Valid datastore types.
    DATASTORES = set(("ApacheLibcloud", "AWS", "Google", "Rackspace", "Filesystem"))

    #: Settings dictionary of accessor callables.
    SETTINGS = {
        # Datastore choice.
        "CLOUD_BROWSER_DATASTORE": Setting(default="Filesystem", valid_set=DATASTORES),
        # Apache Libcloud datastore settings.
        "CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER": Setting(from_env=True),
        "CLOUD_BROWSER_APACHE_LIBCLOUD_ACCOUNT": Setting(from_env=True),
        "CLOUD_BROWSER_APACHE_LIBCLOUD_SECRET_KEY": Setting(from_env=True),
        # Amazon Web Services S3 datastore settings.
        "CLOUD_BROWSER_AWS_ACCOUNT": Setting(from_env=True),
        "CLOUD_BROWSER_AWS_SECRET_KEY": Setting(from_env=True),
        # Google Storage for Developers datastore settings.
        "CLOUD_BROWSER_GS_ACCOUNT": Setting(from_env=True),
        "CLOUD_BROWSER_GS_SECRET_KEY": Setting(from_env=True),
        # Rackspace datastore settings.
        "CLOUD_BROWSER_RACKSPACE_ACCOUNT": Setting(from_env=True),
        "CLOUD_BROWSER_RACKSPACE_SECRET_KEY": Setting(from_env=True),
        "CLOUD_BROWSER_RACKSPACE_SERVICENET": BoolSetting(from_env=True),
        "CLOUD_BROWSER_RACKSPACE_AUTHURL": BoolSetting(from_env=True),
        # Filesystem datastore settings.
        "CLOUD_BROWSER_FILESYSTEM_ROOT": Setting(),
        # View permissions.
        "CLOUD_BROWSER_VIEW_DECORATOR": Setting(),
        # Permissions lists for containers.
        "CLOUD_BROWSER_CONTAINER_WHITELIST": Setting(),
        "CLOUD_BROWSER_CONTAINER_BLACKLIST": Setting(),
        # Browser settings.
        "CLOUD_BROWSER_DEFAULT_LIST_LIMIT": Setting(default=20),
        # Hook for custom actions.
        "CLOUD_BROWSER_OBJECT_REDIRECT_URL": Setting(),
        # Static media root.
        "CLOUD_BROWSER_STATIC_MEDIA_DIR": Setting(),
    }

    def __init__(self):
        """Initializer."""
        self.__container_whitelist = None
        self.__container_blacklist = None

    def __getattr__(self, name, default=None):
        """Get setting."""
        if name in self.SETTINGS:
            return self.SETTINGS[name].get(name, default)

        # Use real Django settings.
        return getattr(_settings, name, default)

    @property
    def _container_whitelist(self):
        """Container whitelist."""
        if self.__container_whitelist is None:
            self.__container_whitelist = set(
                self.CLOUD_BROWSER_CONTAINER_WHITELIST or []
            )
        return self.__container_whitelist

    @property
    def _container_blacklist(self):
        """Container blacklist."""
        if self.__container_blacklist is None:
            self.__container_blacklist = set(
                self.CLOUD_BROWSER_CONTAINER_BLACKLIST or []
            )
        return self.__container_blacklist

    def container_permitted(self, name):
        """Return whether or not a container is permitted.

        :param name: Container name.
        :return: ``True`` if container is permitted.
        :rtype:  ``bool``
        """
        white = self._container_whitelist
        black = self._container_blacklist
        return name not in black and (not white or name in white)

    @property
    def app_media_url(self):
        """Get application media root from real media root URL."""
        url = None
        media_dir = self.CLOUD_BROWSER_STATIC_MEDIA_DIR
        if media_dir:
            url = os.path.join(self.MEDIA_URL, media_dir).rstrip("/") + "/"

        return url

    @property
    def app_media_doc_root(self):  # pylint: disable=R0201
        """Get application media document (file) root."""
        app_dir = os.path.abspath(os.path.dirname(__file__))
        media_root = os.path.join(app_dir, "media")

        return media_root


settings = Settings()  # pylint: disable=C0103
