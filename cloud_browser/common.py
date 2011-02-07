"""Common operations.

Because cloud operations are OS agnostic, we don't use any of :mod:`os` or
:mod:`os.path`.
"""
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured


###############################################################################
# Constants.
###############################################################################
# File-like constants.
#: Browser file path separator.
SEP = "/"
#: Parent path phrase.
PARENT = ".."


###############################################################################
# General.
###############################################################################
def get_int(value, default, test_fn=None):
    """Convert value to integer.

    :param value: Integer value.
    :param default: Default value on failed conversion.
    :param test_fn: Constraint function. Use default if returns ``False``.
    :return: Integer value.
    :rtype:  ``int``
    """
    try:
        converted = int(value)
    except ValueError:
        return default

    test_fn = test_fn if test_fn else lambda x: True
    return converted if test_fn(converted) else default


def check_version(mod, required):
    """Require minimum version of module using ``__version__`` member."""
    vers = tuple(int(v) for v in mod.__version__.split('.')[:3])
    if vers < required:
        req = '.'.join(str(v) for v in required)
        raise ImproperlyConfigured(
            "Module \"%s\" version (%s) must be >= %s." %
            (mod.__name__, mod.__version__, req))


def requires(module, name=""):
    """Enforces module presence.

    The general use here is to allow conditional imports that may fail (e.g., a
    required python package is not installed) but still allow the rest of the
    python package to compile and run fine. If the wrapped method with this
    decorated is invoked, then a runtime error is generated.

    :param module: required module (set as variable to ``None`` on import fail)
    :type  module: ``module`` or ``None``
    :param name: module name
    :type  name: ``string``
    """
    def wrapped(method):
        """Call and enforce method."""
        if module is None:
            raise ImproperlyConfigured("Module '%s' is not installed." % name)
        return method

    return wrapped


###############################################################################
# Date / Time.
###############################################################################
def dt_from_rfc8601(date_str):
    """Convert 8601 (ISO) date string to datetime object.

    Handles "Z" and milliseconds transparently.

    :param date_str: Date string.
    :type  date_str: ``string``
    :return: Date time.
    :rtype:  :class:`datetime.datetime`
    """
    # Normalize string and adjust for milliseconds. Note that Python 2.6+ has
    # ".%f" format, but we're going for Python 2.5, so truncate the portion.
    date_str = date_str.rstrip('Z').split('.')[0]

    # Format string. (2010-04-13T14:02:48.000Z)
    fmt = "%Y-%m-%dT%H:%M:%S"
    # Python 2.6+: Could format and handle milliseconds.
    #if date_str.find('.') >= 0:
    #    fmt += ".%f"

    return datetime.strptime(date_str, fmt)


def dt_from_rfc1123(date_str):
    """Convert 1123 (HTTP header) date string to datetime object.

    :param date_str: Date string.
    :type  date_str: ``string``
    :return: Date time.
    :rtype:  :class:`datetime.datetime`
    """
    fmt = "%a, %d %b %Y %H:%M:%S GMT"
    return datetime.strptime(date_str, fmt)


def dt_from_header(date_str):
    """Try various RFC conversions to ``datetime`` or return ``None``.

    :param date_str: Date string.
    :type  date_str: ``string``
    :return: Date time.
    :rtype:  :class:`datetime.datetime` or ``None``
    """
    convert_fns = (
        dt_from_rfc8601,
        dt_from_rfc1123,
    )

    for convert_fn in convert_fns:
        try:
            return convert_fn(date_str)
        except ValueError:
            pass

    return None


###############################################################################
# Path helpers.
###############################################################################
def basename(path):
    """Rightmost part of path after separator."""
    base_path = path.strip(SEP)
    sep_ind = base_path.rfind(SEP)
    if sep_ind < 0:
        return path

    return base_path[sep_ind+1:]


def path_parts(path):
    """Split path into container, object.

    :param path: Path to resource (including container).
    :type  path: `string`
    :return: Container, storage object tuple.
    :rtype:  `tuple` of `string`, `string`
    """
    path = path if path is not None else ''
    container_path = object_path = ''
    parts = path_list(path)

    if len(parts) > 0:
        container_path = parts[0]
    if len(parts) > 1:
        object_path = path_join(*parts[1:])

    return container_path, object_path


def path_yield(path):
    """Yield on all path parts."""
    for part in (x for x in path.strip(SEP).split(SEP) if x not in (None, '')):
        yield part


def path_list(path):
    """Return list of path parts."""
    return list(path_yield(path))


def path_join(*args):
    """Join path parts to single path."""
    return SEP.join((x for x in args if x not in (None, ''))).strip(SEP)


def relpath(path, start):
    """Get relative path to start.

    Note: Modeled after python2.6 :meth:`os.path.relpath`.
    """
    path_items = path_list(path)
    start_items = path_list(start)

    # Find common parts of path.
    common = []
    for pth, stt in zip(path_items, start_items):
        if pth != stt:
            break
        common.append(pth)

    # Shared parts index in both lists.
    common_ind = len(common)
    parent_num = len(start_items) - common_ind

    # Start with parent traversal and add relative parts.
    rel_items = [PARENT] * parent_num + path_items[common_ind:]
    return path_join(*rel_items)  # pylint: disable=W0142
