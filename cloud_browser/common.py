"""Common operations.

Because cloud operations are OS agnostic, we don't use any of :module:`os` or
:module:`os.path`.
"""

###############################################################################
# Constants.
###############################################################################
SEP = "/"
PARENT = ".."


###############################################################################
# General.
###############################################################################
def get_int(value, default, test_fn=lambda x: True):
    """Convert to integer."""
    try:
        converted = int(value)
    except ValueError:
        return default

    return converted if test_fn(converted) else default


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

    Note: Modeled after python2.6 :method:`os.path.relpath`.
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
