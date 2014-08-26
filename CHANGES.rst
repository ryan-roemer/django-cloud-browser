=========
 Changes
=========

Current
=======
* Fix PyLint, PEP8 issues and upgrade to Django 1.5.
  [`@wxu-urbandaddy <https://github.com/wxu-urbandaddy>`_,
  `@jfk-urbandaddy <https://github.com/jfk-urbandaddy>`_]

v0.2.2
======
* Add dev. requirements, fix URL homepage link.

v0.2.1
======
* Allow fully-qualified string path for ``CLOUD_BROWSER_VIEW_DECORATOR``.
  Thanks to `Branton Davis <https://github.com/bluecamel>`_ for patch.

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
