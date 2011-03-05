"""Cloud browser application.

Provides a simple filesystem-like browser interface for cloud blob datastores.
"""

VERSION = (0, 1, 2, "alpha", 0)

__version__ = ".".join(str(v) for v in VERSION[:3])
__version_full__ = __version__ + "".join(str(v) for v in VERSION[3:])
