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
        folder_obj = conn.get_container(folder_path)

        # List Objects Info Issue:
        #
        # If there are not psuedo-directories, then a `path` parameter to
        # `list_objects_info` will not match any contained folders. On the
        # Other hand, `prefix` parameter matching will always work, but will
        # be overly constrained.
        #
        # We employ the following heuristic. If there is a pseudo-directory
        # at the current level, we **do** use prefix, *else* we use path.

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

        if use_path:
            list_kwargs['path'] = file_path
        else:
            list_kwargs['prefix'] = file_path

        # List files for a folder.
        file_infos = folder_obj.list_objects_info(**list_kwargs)
        for info in file_infos:
            info['path'] = _path_join(folder_path, info['name'])
            info['rel_path'] = info['name'].lstrip(file_path).lstrip('/')

    return render_to_response(template,
                              {'folder': folder_path,
                               'folder_infos': folder_infos,
                               'file': file_path, 'file_infos': file_infos},
                              context_instance=RequestContext(request))
