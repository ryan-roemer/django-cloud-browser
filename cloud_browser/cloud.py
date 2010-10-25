"""Cloud abstractions and helpers."""
# TODO: Add RetryPolicy class.

import os.path

from ConfigParser import SafeConfigParser as ConfigParser

from cloud_browser.errors import ConfigurationError


class Config(object):
    """Cloud configuration."""
    default_path = os.path.expanduser("~/.cloud_browser/cloud.cfg")
    creds_rackspace = 'RackspaceCredentials'
    opt_account = 'account'
    opt_key = 'secret_key'
    opt_servicenet = 'servicenet'

    def __init__(self, account, secret_key, rs_servicenet=False):
        """Initializer."""
        self.account = account
        self.secret_key = secret_key
        self.rs_servicenet = rs_servicenet

        self.__rs_conn_set = False
        self.__rs_conn = None

    @property
    def connection(self):
        """Return Rackspace connection object."""
        import cloudfiles

        if not self.__rs_conn_set:
            self.__rs_conn = cloudfiles.get_connection(
                username=self.account, api_key=self.secret_key,
                servicenet=self.rs_servicenet)
            self.__rs_conn_set = True

        return self.__rs_conn

    @classmethod
    def get_credentials(cls, cfg, section):
        """Get credentials for section type."""
        creds = {
            'account': None,
            'secret_key': None,
        }

        if (cfg.has_section(section) and
                cfg.has_option(section, cls.opt_account) and
                cfg.has_option(section, cls.opt_key)):
            # Basics
            creds['account'] = cfg.get(section, cls.opt_account)
            creds['secret_key'] = cfg.get(section, cls.opt_key)

            # Extras
            if cfg.has_option(section, cls.opt_servicenet):
                creds['rs_servicenet'] = cfg.getboolean(
                    section, cls.opt_servicenet)

        return creds

    @classmethod
    def from_file(cls, config=None):
        """Create configuration from file."""
        if config is None and not os.path.exists(cls.default_path):
            return None

        cfg = ConfigParser()
        if config is None:
            # Default path
            cfg.read(cls.default_path)
        elif isinstance(config, basestring):
            # Filename
            cfg.read(config)
        else:
            # File-like object
            cfg.readfp(config)

        kwargs = cls.get_credentials(cfg, cls.creds_rackspace)

        return cls(**kwargs)    # pylint: disable=W0142

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings."""
        from django.conf import settings

        has_setting = lambda x: getattr(settings, x, None) not in (None, '')

        obj = None
        if (has_setting("CLOUD_BROWSER_ACCOUNT") and
                has_setting("CLOUD_BROWSER_SECRET_KEY")):
            # First try raw settings.
            obj = cls(settings.CLOUD_BROWSER_ACCOUNT,
                      settings.CLOUD_BROWSER_SECRET_KEY,
                      getattr(settings, "CLOUD_BROWSER_SERVICENET", False))

        if obj is None:
            # Then try configuration file.
            obj = cls.from_file(getattr(
                settings, "CLOUD_BROWSER_CONFIG_FILE", None))

        if obj is None:
            raise ConfigurationError("No suitable credentials found.")

        return obj
