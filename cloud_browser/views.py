"""Cloud browser views."""
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

    return parts[0], '/'.join(parts[1:])
    

def browser(request, path='', template="cloud_browser/browser.html"):
    """Basic browser view."""
    folder, file = _path_parts(path)
    folder_infos = None
    file_infos = None
    file_limit = 20
    conn = get_connection()

    if folder == '':
        # List folders.
        folder_infos = conn.list_containers_info()

    else:
        # List files for a folder.
        folder_obj = conn.get_container(folder)
        file_infos = folder_obj.list_objects_info(
            prefix=file, limit=file_limit)
        for info in file_infos:
            info['path'] = '/'.join((folder, info['name']))

    return render_to_response(template,
                              {'folder': folder, 'folder_infos': folder_infos,
                               'file': file, 'file_infos': file_infos},
                              context_instance=RequestContext(request))
