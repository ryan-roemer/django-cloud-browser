"""Cloud abstractions and helpers.

More generally, this is "datastore" support, since the basic interface could
support any interface, file, memory, cloud, etc. But, as this is called a
"cloud" browser, we'll call it the "cloud" module.
"""


def get_connection():
    """Wrapper for global connection/config object."""
    from cloud_browser.cloud.config import Config
    return Config.singleton().connection
