"""Application-specific settings."""
import os
from django.conf import settings as _settings


def _get_setting(name, default=None):
    """Get setting from settings.py."""
    return getattr(_settings, name, default)


def _get_setting_or_env(name, default=None):
    """Get setting from settings.py or environment."""
    # Prefer settings, then environment.
    try:
        return getattr(_settings, name)
    except AttributeError:
        return os.environ.get(name, default)


class Settings(object):
    """Cloud Browser application settings.

    This class wraps the "real" Django settings object, so can be used instead.
    The additional cloud browser settings are as follows:

    **Rackspace**: Configure Rackspace Cloud Files as backing datastore.

    * ``CLOUD_BROWSER_RACKSPACE_ACCOUNT``: Account name.
    * ``CLOUD_BROWSER_RACKSPACE_SECRET_KEY``: Account API secret key.
    * ``CLOUD_BROWSER_RACKSPACE_SERVICENET``: Boolean designating whether or
      not to use Rackspace's servicenet (i.e., the private interface on a
      Cloud Server).

    **Filesystem**: Configure simple filesystem mock datastore.

    * ``CLOUD_BROWSER_FILESYSTEM_ROOT``: Filesystem root to serve from.

    **Container Permissions**: Cloud browser allows a very rudimentary form
    of access control at the container level with white and black lists.
    If the white list is set, only container names in the white list are
    allowed. If the white list is unset, then any container name *not* in
    the black list is permitted. All name matching is exact (no regular
    expressions, etc.).

    * ``CLOUD_BROWSER_CONTAINER_WHITELIST``: White list of names. (Iterable)
    * ``CLOUD_BROWSER_CONTAINER_BLACKLIST``: Black list of names. (Iterable)
    """
    SETTINGS = {
        # Rackspace datastore settings.
        'CLOUD_BROWSER_RACKSPACE_ACCOUNT': _get_setting_or_env,
        'CLOUD_BROWSER_RACKSPACE_SECRET_KEY': _get_setting_or_env,
        'CLOUD_BROWSER_RACKSPACE_SERVICENET': _get_setting_or_env,

        # Filesystem datastore settings.
        'CLOUD_BROWSER_FILESYSTEM_ROOT': _get_setting,

        # Permissions lists for containers.
        'CLOUD_BROWSER_CONTAINER_WHITELIST': _get_setting,
        'CLOUD_BROWSER_CONTAINER_BLACKLIST': _get_setting,
    }

    def __init__(self):
        """Initializer."""
        self.__container_whitelist = None
        self.__container_blacklist = None

    def __getattr__(self, name, default=None):
        """Get setting."""
        if name in self.SETTINGS:
            return self.SETTINGS[name](name, default)

        # Use real Django settings.
        return getattr(_settings, name, default)

    @property
    def _container_whitelist(self):
        """Container whitelist."""
        if self.__container_whitelist is None:
            self.__container_whitelist = \
                set(self.CLOUD_BROWSER_CONTAINER_WHITELIST or [])
        return self.__container_whitelist

    @property
    def _container_blacklist(self):
        """Container blacklist."""
        if self.__container_blacklist is None:
            self.__container_blacklist = \
                set(self.CLOUD_BROWSER_CONTAINER_BLACKLIST or [])
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


settings = Settings()  # pylint: disable=C0103