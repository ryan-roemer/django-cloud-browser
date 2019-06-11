=========
 Changes
=========

v0.5.1
======
* Fix filesystem backend on Windows.
  [`@c-w <https://github.com/c-w>`_]

v0.5.0
======
* Add support for more cloud backends via Apache libcloud.
  [`@c-w <https://github.com/c-w>`_]
* Fix install on Python 3.6+
  [`@c-w <https://github.com/c-w>`_]

v0.4.0
======
* Various updates for Django 1.8+ and Python 3.
  [`@corcoran <https://github.com/corcoran>`_]

v0.3.0
======
* Various updates for Django 1.8.
  [`@sysradium <https://github.com/sysradium>`_]

v0.2.3
======
* Fix deprecated ``django.conf.urls.defaults``.
  [`@Anton-Shutik <https://github.com/Anton-Shutik>`_]
* Fix PyLint, PEP8 issues and upgrade to Django 1.5.
  [`@wxu-urbandaddy <https://github.com/wxu-urbandaddy>`_,
  `@jfk-urbandaddy <https://github.com/jfk-urbandaddy>`_]

v0.2.2
======
* Add dev. requirements, fix URL homepage link.

v0.2.1
======
* Allow fully-qualified string path for ``CLOUD_BROWSER_VIEW_DECORATOR``.
  [`@bluecamel <https://github.com/bluecamel>`_]

v0.2.0
======
* Add Google Storage for Developers datastore support.
* Start significant CSS refactoring.

v0.1.3
======
* Cleaned up ``sdist`` packagin.
* Added basic file icons and images to static media.
* Switch application static media to use straight Django
  ``django.views.static.serve`` wrapper instead of custom system.

v0.1.2
======
* Added support for `OpenStack <http://www.openstack.org/>`_.
  [`@noodley <https://github.com/noodley>`_]

v0.1.1
======
* Initial tarball release. Basic support for AWS, Rackspace, filesystem
  datastores, and basic and admin views.
