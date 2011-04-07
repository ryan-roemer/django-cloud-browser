"""Cloud browser application.

Provides a simple filesystem-like browser interface for cloud blob datastores.
"""

VERSION = (0, 2, 0, "alpha", 1)

__version__ = ".".join(str(v) for v in VERSION[:3])
__version_full__ = __version__ + "".join(str(v) for v in VERSION[3:])
