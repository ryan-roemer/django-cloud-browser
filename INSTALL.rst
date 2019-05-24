==============
 Installation
==============


Install
=======

Cloud Browser can be installed from PyPi or from GitHub.

PyPi
----
Basic installation::

    pip install django-cloud-browser

Versioned
---------
Install a specific version (where ``<VERSION>`` is something like "|version|")
from PyPi::

    pip install django-cloud-browser==<VERSION>

or from GitHub::

    pip install https://github.com/ryan-roemer/django-cloud-browser/zipball/v<VERSION>

Development
-----------
Install the Cloud Browser package from current development source::

    pip install https://github.com/ryan-roemer/django-cloud-browser/tarball/master

or::

    pip install -e git://github.com/ryan-roemer/django-cloud-browser#egg=cloud_browser

Software Requirements
=====================

Cloud Browser uses conditional imports to only actually require other libraries
that are used in the active configuration. Loosely speaking, for deployment,
only the following is actually needed:

* Python 2.7 or Python 3.6
* `Django <http://www.djangoproject.com/>`_

The application relies on third party open source libraries to actually
communicate with cloud datastores, so for each cloud datastore you need the
corresponding library below:

* Apache Libcloud: `apache-libcloud <https://pypi.org/project/apache-libcloud/>`_
* Amazon S3 / Google Storage: `boto <http://code.google.com/p/boto/>`_
* Rackspace Cloud Files / OpenStack Storage:
  `cloudfiles <https://github.com/rackspace/python-cloudfiles>`_
  (version 1.7.4+ is required).

.. _install_basic:

Configuration
=============
All configuration options are fully described in the
:ref:`application settings <app_settings>` documentation.

Here is a quick start example for Rackspace Cloud Files:

Settings
--------
First, start with edits to your Django project's ``settings.py``::

    INSTALLED_APPS = (
        # ...
        'cloud_browser',
    )

    CLOUD_BROWSER_DATASTORE = "Rackspace"
    CLOUD_BROWSER_RACKSPACE_ACCOUNT = "<my_account>"
    CLOUD_BROWSER_RACKSPACE_SECRET_KEY = "<my_secret_key>"

In addition, for more security options, the following Cloud Browser options
may be set via environment variables instead of ``settings.py`` variables:

* ``CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER``
* ``CLOUD_BROWSER_APACHE_LIBCLOUD_ACCOUNT``
* ``CLOUD_BROWSER_APACHE_LIBCLOUD_SECRET_KEY``
* ``CLOUD_BROWSER_AWS_ACCOUNT``
* ``CLOUD_BROWSER_AWS_SECRET_KEY``
* ``CLOUD_BROWSER_GS_ACCOUNT``
* ``CLOUD_BROWSER_GS_SECRET_KEY``
* ``CLOUD_BROWSER_RACKSPACE_ACCOUNT``
* ``CLOUD_BROWSER_RACKSPACE_SECRET_KEY``
* ``CLOUD_BROWSER_RACKSPACE_SERVICENET``
* ``CLOUD_BROWSER_RACKSPACE_AUTHURL``

in the form of::

    $ export CLOUD_BROWSER_<Setting Name>="<value>"

Other settings you may wish to investigate include:

* Container white/black lists: Control access to containers.

  * ``CLOUD_BROWSER_CONTAINER_WHITELIST``
  * ``CLOUD_BROWSER_CONTAINER_BLACKLIST``

* ``CLOUD_BROWSER_DEFAULT_LIST_LIMIT``: Default number of objects to display
  per browser page.

URLs
----
Next, add the URLs to your ``urls.py``::

    urlpatterns = patterns('',
        # ...
        url(r'^cb/', include('cloud_browser.urls')),
    )

.. _install_admin:

Admin Configuration
===================
Cloud Browser also supports integration with the Django admin, for cases in
which only admin users get to access the datastore. Separate templates, as
well as built-in Django admin resources are used for a consistent admin
experience.

.. note::
    This is not a "full" Django application, just a modest hack (with some
    JavaScript trickery) to make the Cloud Browser appear like a normal
    administrative application. And, unfortunately there is no link off
    the admin index page (although you could extend the Django admin index
    template to include this without too much hassle).

Settings
--------
In addition to the general settings above, the settings variable
``CLOUD_BROWSER_VIEW_DECORATOR`` should be set to ``staff_member_required`` to
match the rest of the administrative permissions::

    from django.contrib.admin.views.decorators import staff_member_required
    CLOUD_BROWSER_VIEW_DECORATOR = staff_member_required

Alternatively, a fully-qualified string path can be used like::

    CLOUD_BROWSER_VIEW_DECORATOR = \
        "django.contrib.admin.views.decorators.staff_member_required"

URLs
----
Cloud Browser has a separate set of templates and URLs for use in with the
admin. Here's a suggested setup::

    urlpatterns = patterns('',
        # ...

        # Place Cloud Browser URLs **before** admin.
        url(r'^admin/cb/', include('cloud_browser.urls_admin')),

        # Admin URLs.
        url(r'^admin/', include(admin.site.urls)),
    )

Static Media
============
The Cloud Browser application relies on a modest amount of CSS and JavaScript.
By default, the static media is served by a Django static view, as this is the
most compatible approach (and has no further configuration).

However, this is not efficient, as the static media files should be
separately statically served. If you separately serve the Cloud Browser static
media directory, the application will use links instead of inline code dumps.
To enable this, simply symlink the Cloud Browser static media directory to
wherever your static media is served from (in this case "/path/to/static_media"
is the ``MEDIA_ROOT``)::

    $ cd /path/to/static_media
    $ ln -s /path/to/cloud_browser/templates/cloud_browser_media cloud_browser

(in this case a "cloud_browser" symlink), and then add the relative path from
your ``MEDIA_ROOT`` to the following ``settings.py`` variable::

    CLOUD_BROWSER_STATIC_MEDIA_DIR = "cloud_browser"

And all of the Cloud Browser media is actually *statically* served.

Examples
========
The source contains an `example project`_ that is configures and serves up the
Cloud Browser application, and little more. It is a good starting point if you
are having difficulties getting things going.

.. _`example project`: https://github.com/ryan-roemer/django-cloud-browser/
  blob/master/cloud_browser_project
