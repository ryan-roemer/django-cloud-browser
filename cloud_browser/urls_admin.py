"""Cloud browser URLs for Django admin integration."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from cloud_browser.app_settings import settings

# pylint: disable=invalid-name
urlpatterns = patterns(
    'cloud_browser.views',
    url(r'^$',
        # pylint: disable=no-value-for-parameter
        RedirectView.as_view(url='browser'),
        name="cloud_browser_index"),
    url(r'^browser/(?P<path>.*)$', 'browser', name="cloud_browser_browser",
        kwargs={'template': "cloud_browser/admin/browser.html"}),
    url(r'^document/(?P<path>.*)$', 'document', name="cloud_browser_document"),
)

if settings.app_media_url is None:
    # Use a static serve.
    urlpatterns += patterns(
        '',
        url(r'^app_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.app_media_doc_root},
            name="cloud_browser_media"),
    )
