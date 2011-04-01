from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.defaults import (  # pylint: disable=W0611
    handler404, handler500)
from django.contrib import admin
from django.views.generic.simple import redirect_to

# Enable admin.
admin.autodiscover()

ADMIN_URLS = False
urlpatterns = patterns('')  # pylint: disable=C0103

if ADMIN_URLS:
    urlpatterns += patterns('',
        # Admin URLs. Note: Include ``urls_admin`` **before** admin.
        url(r'^$', redirect_to, name='index', kwargs={'url': 'admin/'}),
        url(r'^admin/cb/', include('cloud_browser.urls_admin')),
    )

else:
    urlpatterns += patterns('',
        # Normal URLs.
        url(r'^$', redirect_to, name='index', kwargs={'url': 'cb/'}),
        url(r'^cb/', include('cloud_browser.urls')),
    )

urlpatterns += patterns('',
    # Hack in the bare minimum to get accounts support.
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/$', redirect_to, kwargs={'url': 'login'}),
    url(r'^accounts/profile', redirect_to, kwargs={'url': '/'}),
)

if settings.DEBUG:
    # Serve up static media.
    urlpatterns += patterns('',
        url(r'^' + settings.MEDIA_URL.strip('/') + '/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
