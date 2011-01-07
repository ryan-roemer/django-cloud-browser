"""Cloud abstractions and helpers."""


def get_connection():
    """Wrapper for global connection/config object."""
    from cloud_browser.cloud.config import Config
    return Config.singleton().connection.connection
