from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('cloud_browser.views',
    url(r'^$', redirect_to, name="cloud_browser_index", kwargs={'url': 'browser'}),
    url(r'browser/$', 'browser', name="cloud_browser_browser"),
)
