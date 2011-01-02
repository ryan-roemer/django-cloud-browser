"""Application-specific settings."""
import os
from django.conf import settings as _settings


def _get_setting_or_env(name, default=None):
    """Get setting from settings.py or environment."""
    # Prefer settings, then environment.
    try:
        return getattr(_settings, name)
    except AttributeError:
        return os.environ.get(name, default)


class Settings(object):
    """Cloud Browser application settings.

    Class wraps the "real" Django settings object, so can be used instead.
    """
    SETTINGS = {
        'CLOUD_BROWSER_RACKSPACE_ACCOUNT': _get_setting_or_env,
        'CLOUD_BROWSER_RACKSPACE_SECRET_KEY': _get_setting_or_env,
        'CLOUD_BROWSER_RACKSPACE_SERVICENET': _get_setting_or_env,
    }

    def __getattr__(self, name, default=None):
        """Get setting."""
        if name in self.SETTINGS:
            return self.SETTINGS[name](name)

        # Use real Django settings.
        return getattr(_settings, name)

settings = Settings()  # pylint: disable=C0103
