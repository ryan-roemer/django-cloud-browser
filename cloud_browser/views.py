"""Cloud browser views."""
# TODO: Need to add directory "application/directory" markers everywhere.
# Probably should consider writing a stupid crawler.

import cloudfiles
import os

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


def _get_files2(folder_obj, folder_path, file_path):
    """Get files."""

    file_limit = 20
    file_path = file_path + '/' if file_path else ''
    file_infos = folder_obj.list_objects_info(
        limit=file_limit, delimiter='/', prefix=file_path)

    for info in (i for i in file_infos if i.get('subdir', None)):
        info['name'] = info['subdir']
    for info in file_infos:
        info['path'] = _path_join(folder_path, info['name'])
        info['rel_path'] = _relpath(info['name'], file_path)

    return file_infos


def _get_files(folder_obj, folder_path, file_path):
    """Get files."""
    # List Objects Info Issue:
    #
    # If there are not psuedo-directories, then a `path` parameter to
    # `list_objects_info` will not match any contained folders. On the
    # Other hand, `prefix` parameter matching will always work, but will
    # be overly constrained.
    #
    # We employ the following heuristic. If there is a pseudo-directory
    # at the current level, we **do** use prefix, *else* we use path.

    file_limit = 20
    list_kwargs = {
        'limit': file_limit,
    }

    use_path = False
    if file_path != '':
        try:
            file_obj = folder_obj.get_object(file_path)
            use_path = file_obj.content_type == 'application/directory'
        except cloudfiles.errors.NoSuchObject:
            pass

    if use_path or file_path == '':
        list_kwargs['path'] = file_path
    else:
        list_kwargs['prefix'] = file_path

    # List files for a folder.
    file_infos = folder_obj.list_objects_info(  # pylint: disable=W0142
        **list_kwargs)
    for info in file_infos:
        info['path'] = _path_join(folder_path, info['name'])
        info['rel_path'] = _relpath(info['name'], file_path)

    return file_infos


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
    folder_path, file_path = _path_parts(path)
    folder_infos = None
    file_infos = None
    conn = get_connection()

    if folder_path == '':
        # List folders.
        folder_infos = conn.list_containers_info()

    else:
        folder_obj = conn.get_container(folder_path)
        file_infos = _get_files2(folder_obj, folder_path, file_path)

    return render_to_response(template,
                              {'path': path,
                               'folder': folder_path,
                               'folder_infos': folder_infos,
                               'file': file_path,
                               'file_infos': file_infos},
                              context_instance=RequestContext(request))
