==============
 Installation
==============

Install the Cloud Browser package from source::

    pip install -e git://github.com/ryan-roemer/django-cloud-browser#egg=cloud_browser

In the future, we'll look to add:

* Github tarballs.
* PyPi registration.

Software Requirements
=====================

Cloud Browser uses conditional imports to only actually require other libraries
that are used in the active configuration. Loosely speaking, for deployment,
only the following is actually needed:

* Python 2.5+
* `Django <http://www.djangoproject.com/>`_

The application relies on third party open source libraries to actually
communicate with cloud datastores, so for each cloud datastore you need the
corresponding library below:

* Amazon S3: `boto <http://code.google.com/p/boto/>`_
* Rackspace Cloud Files:
  `cloudfiles <https://github.com/rackspace/python-cloudfiles>`_
  (version 1.7.4+ is required).

Configuration
=============
All configuration options are described in the 
:ref:`application settings <app_settings>` documentation.

Here is a quick start example for Rackspace Cloud Files:

Settings
--------
First, start with edits to your Django project's ``settings.py``::

    INSTALLED_APPS = (
        # ...
        'cloud_browser',
    )

    CLOUD_BROWSER_RACKSPACE_ACCOUNT = "<my_account>"
    CLOUD_BROWSER_RACKSPACE_SECRET_KEY = "<my_secret_key>"

Other settings you may wish to investigate include:

* Container white/black lists: Control access to containers.

  * ``CLOUD_BROWSER_CONTAINER_WHITELIST``
  * ``CLOUD_BROWSER_CONTAINER_BLACKLIST``

* ``CLOUD_BROWSER_DEFAULT_LIST_LIMIT``: Default number of objects to diplay
  per browser page.

URLs
----
Next, add the URLs to your ``urls.py``::

    urlpatterns = patterns('',
        # ...
        url(r'^cb/', include('cloud_browser.urls')),
    )

Static Media
============
The Cloud Browser application relies on a modest amount of CSS and JavaScript.
By default, the static media is included inline into HTML views as full script,
as this is the most compatible approach (and has no further configuration).

However, this is not efficient, as the CSS and JavaScript files should be
separately staticly served. If you separately serve up the Cloud Browser static
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
