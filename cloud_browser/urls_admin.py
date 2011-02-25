"""Cloud browser URLs for Django admin integration."""
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('cloud_browser.views',  # pylint: disable=C0103
    url(r'^$', redirect_to, name="cloud_browser_index",
        kwargs={'url': 'browser'}),
    url(r'^browser/(?P<path>.*)$', 'browser', name="cloud_browser_browser",
        kwargs={'template': "cloud_browser/admin/browser.html"}),
    url(r'^document/(?P<path>.*)$', 'document', name="cloud_browser_document"),
)
