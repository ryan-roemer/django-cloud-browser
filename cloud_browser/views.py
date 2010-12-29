"""Cloud browser views."""
import cloudfiles as cf

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from cloud_browser.common import SEP, path_parts, path_join, path_yield
from cloud_browser.cloud import get_connection, CloudObject


def _get_objects(container_obj, object_path):
    """Get object information."""

    object_limit = 20
    object_path = object_path + SEP if object_path else ''
    object_infos = container_obj.list_objects_info(
        limit=object_limit, delimiter=SEP, prefix=object_path)

    return [CloudObject.from_info(container_obj, x) for x in object_infos]


def _breadcrumbs(path):
    """Return breadcrumb dict from path."""

    full = None
    crumbs = []
    for part in path_yield(path):
        full = path_join(full, part) if full else part
        crumbs.append((full, part))

    return crumbs


def browser(request, path='', template="cloud_browser/browser.html"):
    """View files in a file path.

    :param request: The request.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """
    container_path, object_path = path_parts(path)
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

        object_infos = _get_objects(container_obj, object_path)
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


def view(request, path=''):
    """View single file from path.

    :param request: The request.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """
    import mimetypes

    container_path, object_path = path_parts(path)
    conn = get_connection()
    try:
        container_obj = conn.get_container(container_path)
    except cf.errors.NoSuchContainer:
        raise Http404("No container at: %s" % container_path)

    try:
        file_obj = container_obj.get_object(object_path)
    except cf.errors.NoSuchObject:
        raise Http404("No object at: %s" % object_path)

    content_type = file_obj.content_type
    guessed_type, encoding = mimetypes.guess_type(file_obj.name)
    if content_type in (None, '', 'application/octet-stream'):
        content_type = guessed_type

    response = HttpResponse(content=file_obj.read(),
                            content_type=content_type)

    # Check if compression allowed. If so, set up pass through
    use_gzip = 'gzip' in request.META.get("HTTP_ACCEPT_ENCODING", '')
    if use_gzip and encoding == 'gzip':
        response['Content-Encoding'] = 'gzip'

    return response
