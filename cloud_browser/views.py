"""Cloud browser views."""
import os
import cloudfiles as cf

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from cloud_browser.cloud import get_connection


def _path_parts(path=''):
    """Split path into folder, file tuple."""
    path = path if path is not None else ''
    parts = path.strip('/').split('/')
    if len(parts) == 1:
        return parts[0], ''

    return parts[0], _path_join(*parts[1:])


def _path_join(*args):
    """Custom path joining."""
    return '/'.join((x for x in args if x not in (None, '')))


def _relpath(path, start=os.curdir):
    """Get relative path to start.

    Note: Modeled after python2.6 version.
    """

    # Helpers.
    slash = "/"
    parent = ".."

    path_parts = os.path.abspath(path).split(slash)
    start_parts = os.path.abspath(start).split(slash)
    common = os.path.commonprefix([start_parts, path_parts])

    # Shared parts index in both lists.
    shared_ind = len(common)
    parent_num = len(start_parts) - shared_ind

    # Start with parent traversal and add relative parts.
    rel_parts = [parent] * parent_num + path_parts[shared_ind:]
    if not rel_parts:
        return os.curdir

    return os.path.join(*rel_parts)  # pylint: disable=W0142


def _get_object_infos(container_obj, object_path):
    """Get object information."""

    object_limit = 20
    object_path = object_path + '/' if object_path else ''
    object_infos = container_obj.list_objects_info(
        limit=object_limit, delimiter='/', prefix=object_path)

    # Add extra information for subdir's.
    for info in (i for i in object_infos if i.get('subdir', None)):
        info['name'] = info['subdir']
        info['is_file'] = False

    # Add path information for all infos.
    for info in object_infos:
        info['path'] = _path_join(container_obj.name, info['name'])
        info['rel_path'] = _relpath(info['name'], object_path)
        info['is_file'] = info.get('is_file', True)

    return object_infos


def _breadcrumbs(path):
    """Return breadcrumb dict from path."""

    full = None
    crumbs = []
    if path:
        for part in path.strip('/').split('/'):
            full = os.path.join(full, part) if full else part
            crumbs.append((full, part))

    return crumbs


def browser(request, path='', template="cloud_browser/browser.html"):
    """View files in a file path.

    Note the viewing results are different whether or not there is a
    pseudo-directory marker present. If there is a not a pseudo-directory
    up to the current level, we use a "prefix" match instead.

    This ambiguity can be most properly addressed by adding pseudo-directory
    markers for all file objects.

    :param request: The request.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """
    container_path, object_path = _path_parts(path)
    container_infos = None
    object_infos = None
    conn = get_connection()

    if container_path == '':
        # List containers.
        container_infos = conn.list_containers_info()

    else:
        try:
            container_obj = conn.get_container(container_path)
        except cf.errors.NoSuchContainer:
            raise Http404("No container at: %s" % container_path)

        object_infos = _get_object_infos(container_obj, object_path)
        if not object_infos:
            raise Http404("No objects at: %s" % object_path)

        # TODO: Have a 'view object' if get single object succeeds.

    return render_to_response(template,
                              {'path': path,
                               'breadcrumbs': _breadcrumbs(path),
                               'container_path': container_path,
                               'container_infos': container_infos,
                               'object_path': object_path,
                               'object_infos': object_infos},
                              context_instance=RequestContext(request))
