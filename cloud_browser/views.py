"""Cloud browser views."""
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from cloud_browser.cloud import get_connection, errors
from cloud_browser.common import path_parts, path_join, path_yield, get_int


DEFAULT_LIMIT = 20


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
    from itertools import ifilter, islice

    # Inputs.
    container_path, object_path = path_parts(path)
    marker = request.GET.get('marker', None)
    limit = get_int(request.GET.get('limit', DEFAULT_LIMIT),
                    DEFAULT_LIMIT,
                    lambda x: x > 0 and x < 10000 - 1)

    # Q1: Get all containers.
    #     We optimize here by not individually looking up containers later,
    #     instead going through this in-memory list.
    # TODO: Check if this is too expensive network and results-wise.
    conn = get_connection()
    containers = conn.get_containers()

    container = None
    objects = None
    if container_path != '':
        # Find marked container from list.
        cont_eq = lambda c: c.name == container_path
        cont_list = list(islice(ifilter(cont_eq, containers), 1))
        if not cont_list:
            raise Http404("No container at: %s" % container_path)

        # Q2: Get objects for instant list, plus one to check "next".
        container = cont_list[0]
        objects = container.get_objects(object_path, marker, limit+1)
        marker = None

        # If over limit, strip last item and set marker.
        if len(objects) == limit + 1:
            objects = objects[:limit]
            marker = objects[-1].name

    return render_to_response(template,
                              {'path': path,
                               'marker': marker,
                               'limit': limit,
                               'breadcrumbs': _breadcrumbs(path),
                               'container_path': container_path,
                               'containers': containers,
                               'container': container,
                               'object_path': object_path,
                               'objects': objects},
                              context_instance=RequestContext(request))


def document(_, path=''):
    """View single document from path.

    :param path: Path to resource, including container as first part of path.
    """
    container_path, object_path = path_parts(path)
    conn = get_connection()
    try:
        container = conn.get_container(container_path)
    except errors.NoContainerException:
        raise Http404("No container at: %s" % container_path)
    except errors.NotPermittedException:
        raise Http404("Access denied for container at: %s" % container_path)

    try:
        storage_obj = container.get_object(object_path)
    except errors.NoObjectException:
        raise Http404("No object at: %s" % object_path)

    # Get content-type and encoding.
    content_type = storage_obj.smart_content_type
    encoding = storage_obj.smart_content_encoding
    response = HttpResponse(content=storage_obj.read(),
                            content_type=content_type)
    if encoding not in (None, ''):
        response['Content-Encoding'] = encoding

    return response
