"""Cloud browser views."""
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


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
    return render_to_response(template,
                              {'folder': folder, 'file': file},
                              context_instance=RequestContext(request))
