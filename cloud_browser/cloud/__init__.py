"""Cloud abstractions and helpers.

More generally, this is "datastore" support, since the basic interface could
support any interface, file, memory, cloud, etc. But, as this is called a
"cloud" browser, we'll call it the "cloud" module.
"""


def get_connection():
    """Return global connection object.

    :rtype: :class:`cloud_browser.cloud.base.CloudConnection`
    """
    from cloud_browser.cloud.config import Config
    return Config.get_connection()


def get_connection_cls():
    """Return global connection class.

    :rtype: :class:`type`
    """
    from cloud_browser.cloud.config import Config
    return Config.get_connection_cls()
