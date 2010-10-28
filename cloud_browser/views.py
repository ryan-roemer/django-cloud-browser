"""Cloud browser views."""
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


def browser(request, template="cloud_browser/browser.html"):
    """Basic browser view."""
    return render_to_response(template,
                              context_instance=RequestContext(request))
