"""Cloud browser views."""
import cloudfiles as cf

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from cloud_browser.common import SEP, path_parts, path_join, path_yield, \
    get_int
from cloud_browser.cloud import get_connection, CloudObject


DEFAULT_LIMIT = 20


def _get_objects(container_obj, object_path, marker=None, limit=20):
    """Get object information."""

    object_path = object_path + SEP if object_path else ''
    object_infos = container_obj.list_objects_info(
        limit=limit, delimiter=SEP, prefix=object_path, marker=marker)

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
    # Inputs.
    container_path, object_path = path_parts(path)
    marker = request.GET.get('marker', None)
    limit = get_int(request.GET.get('limit', DEFAULT_LIMIT),
                    DEFAULT_LIMIT,
                    lambda x: x > 0 and x < 10000 - 1)

    # Other variables.
    container_infos = None
    object_infos = None
    conn = get_connection()

    if container_path == '':
        # List containers.
        container_infos = conn.list_containers_info()

    else:
        # Q1: Get the container.
        try:
            container_obj = conn.get_container(container_path)
        except cf.errors.NoSuchContainer:
            raise Http404("No container at: %s" % container_path)

        # Q2: Get objects for instant list, plus one to check "next".
        object_infos = _get_objects(
            container_obj, object_path, marker, limit+1)
        marker = None

        if not object_infos:
            # Try the view document instead.
            return document(request, path)

        # If over limit, strip last item and set marker.
        elif len(object_infos) == limit + 1:
            object_infos = object_infos[:limit]
            marker = object_infos[-1].name

    return render_to_response(template,
                              {'path': path,
                               'marker': marker,
                               'limit': limit,
                               'breadcrumbs': _breadcrumbs(path),
                               'container_path': container_path,
                               'container_infos': container_infos,
                               'object_path': object_path,
                               'object_infos': object_infos},
                              context_instance=RequestContext(request))


def document(_, path=''):
    """View single document from path.

    :param path: Path to resource, including container as first part of path.
    """
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

    # Get content-type and encoding.
    storage_obj = CloudObject.from_obj(container_obj, file_obj)
    content_type = storage_obj.smart_content_type
    encoding = storage_obj.smart_content_encoding
    response = HttpResponse(content=file_obj.read(), content_type=content_type)
    if encoding not in (None, ''):
        response['Content-Encoding'] = encoding

    return response
