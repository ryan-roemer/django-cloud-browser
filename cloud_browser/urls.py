"""Cloud browser URLs."""
from django.conf.urls import url
from django.views.static import serve

from cloud_browser.app_settings import settings
from cloud_browser.views import browser, document, index

# pylint: disable=invalid-name
urlpatterns = [
    url(r"^$", index, name="cloud_browser_index"),
    url(r"^browser/(?P<path>.*)$", browser, name="cloud_browser_browser"),
    url(r"^document/(?P<path>.*)$", document, name="cloud_browser_document"),
]

if settings.app_media_url is None:
    # Use a static serve.
    urlpatterns += [
        url(
            r"^app_media/(?P<path>.*)$",
            serve,
            {"document_root": settings.app_media_doc_root},
            name="cloud_browser_media",
        )
    ]
