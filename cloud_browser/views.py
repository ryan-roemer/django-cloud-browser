"""Cloud browser views."""
import json

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlencode

from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, get_connection, get_connection_cls
from cloud_browser.common import get_int, path_join, path_parts, path_yield, relpath

try:
    # pylint: disable=no-name-in-module, import-error, ungrouped-imports
    from django.utils.importlib import import_module
except ImportError:
    from importlib import import_module


MAX_LIMIT = get_connection_cls().cont_cls.max_list


def settings_view_decorator(function):
    """Insert decorator from settings, if any.

    .. note:: Decorator in ``CLOUD_BROWSER_VIEW_DECORATOR`` can be either a
        callable or a fully-qualified string path (the latter, which we'll
        lazy import).
    """

    dec = settings.CLOUD_BROWSER_VIEW_DECORATOR

    # Trade-up string to real decorator.
    if isinstance(dec, str):
        # Split into module and decorator strings.
        mod_str, _, dec_str = dec.rpartition(".")
        if not (mod_str and dec_str):
            raise ImportError("Unable to import module: %s" % mod_str)

        # Import and try to get decorator function.
        mod = import_module(mod_str)
        if not hasattr(mod, dec_str):
            raise ImportError("Unable to import decorator: %s" % dec)

        dec = getattr(mod, dec_str)

    if dec and callable(dec):
        return dec(function)

    return function


def _breadcrumbs(path):
    """Return breadcrumb dict from path."""

    full = None
    crumbs = []
    for part in path_yield(path):
        full = path_join(full, part) if full else part
        crumbs.append((full, part))

    return crumbs


def _get_context_data(request):
    try:
        return json.loads(request.session["context_data"])
    except (AttributeError, KeyError):
        return {}


def _set_context_data(request):
    try:
        request.session["context_data"] = json.dumps(request.GET.dict())
    except AttributeError:
        pass


def index(request):
    """Stash context data in the session and redirect to the cloud browser.

    The context data will be passed to the custom view function when exiting
    the cloud browser context.

    :param request: The request.
    """
    _set_context_data(request)
    return redirect("cloud_browser_browser", path="")


@settings_view_decorator
def browser(request, path="", template="cloud_browser/browser.html"):
    """View files in a file path.

    :param request: The request.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """

    from itertools import islice

    try:
        # pylint: disable=redefined-builtin
        from future_builtins import filter
    except ImportError:
        # pylint: disable=import-error
        from builtins import filter

    # Inputs.
    container_path, object_path = path_parts(path)
    incoming = request.POST or request.GET or {}

    marker = incoming.get("marker", None)
    marker_part = incoming.get("marker_part", None)
    if marker_part:
        marker = path_join(object_path, marker_part)

    # Get and adjust listing limit.
    limit_default = settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT

    def limit_test(num):
        return num > 0 and (MAX_LIMIT is None or num <= MAX_LIMIT - 1)

    limit = get_int(incoming.get("limit", limit_default), limit_default, limit_test)

    # Q1: Get all containers.
    #     We optimize here by not individually looking up containers later,
    #     instead going through this in-memory list.
    # TODO: Should page listed containers with a ``limit`` and ``marker``.
    conn = get_connection()
    containers = conn.get_containers()

    marker_part = None
    container = None
    objects = None
    if container_path != "":
        # Find marked container from list.
        def cont_eq(container):
            return container.name == container_path

        filtered_conts = filter(cont_eq, containers)
        cont_list = list(islice(filtered_conts, 1))
        if not cont_list:
            raise Http404("No container at: %s" % container_path)

        # Q2: Get objects for instant list, plus one to check "next".
        container = cont_list[0]
        objects = container.get_objects(object_path, marker, limit + 1)
        marker = None

        # If over limit, strip last item and set marker.
        if len(objects) == limit + 1:
            objects = objects[:limit]
            marker = objects[-1].name
            marker_part = relpath(marker, object_path)

    return render(
        request,
        template,
        {
            "path": path,
            "marker": marker,
            "marker_part": marker_part,
            "limit": limit,
            "breadcrumbs": _breadcrumbs(path),
            "container_path": container_path,
            "containers": containers,
            "container": container,
            "object_path": object_path,
            "objects": objects,
        },
    )


@settings_view_decorator
def document(request, path=""):
    """View single document from path.

    :param request: The request.
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

    custom_view = settings.CLOUD_BROWSER_OBJECT_REDIRECT_URL
    if custom_view:
        separator = "?" if "?" not in custom_view else "&"
        params = {"container": container_path, "object": object_path}
        params.update(_get_context_data(request))
        return redirect(custom_view + separator + urlencode(params))

    # Get content-type and encoding.
    content_type = storage_obj.smart_content_type
    encoding = storage_obj.smart_content_encoding
    response = HttpResponse(content=storage_obj.read(), content_type=content_type)
    if encoding not in (None, ""):
        response["Content-Encoding"] = encoding

    return response
