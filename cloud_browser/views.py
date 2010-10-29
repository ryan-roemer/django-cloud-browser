"""Cloud browser views."""
# TODO: Need to add directory "application/directory" markers everywhere.
# Probably should consider writing a stupid crawler.

import os.path

from django.http import HttpResponse, HttpResponseNotFound, Http404
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

def browser(request, path='', template="cloud_browser/browser.html"):
    """Basic browser view."""
    folder_path, file_path = _path_parts(path)
    folder_infos = None
    file_infos = None
    file_limit = 20
    conn = get_connection()

    if folder_path == '':
        # List folders.
        folder_infos = conn.list_containers_info()

    else:
        # List files for a folder.
        folder_obj = conn.get_container(folder_path)
        file_infos = folder_obj.list_objects_info(
            path=file_path, limit=file_limit)
        for info in file_infos:
            info['path'] = _path_join(folder_path, info['name'])
            info['rel_path'] = info['name'].lstrip(file_path).lstrip('/')

    return render_to_response(template,
                              {'folder': folder_path,
                               'folder_infos': folder_infos,
                               'file': file_path, 'file_infos': file_infos},
                              context_instance=RequestContext(request))
