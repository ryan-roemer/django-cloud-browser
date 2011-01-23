from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.defaults import (  # pylint: disable=W0611
    handler404, handler500)
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',  # pylint: disable=C0103
    url(r'^$', redirect_to, name='index', kwargs={'url': 'cb/'}),
    url(r'^cb/', include('cloud_browser.urls')),
)

if settings.DEBUG:
    # Serve up static media.
    urlpatterns += patterns('',
        url(r'^' + settings.MEDIA_URL.strip('/') + '/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
