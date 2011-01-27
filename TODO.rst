==================
 TODO / Task List
==================

Current
=======

* Add AWS.
* Add license.
* Finish README.rst, INSTALL.rst.

Logistics
=========

* **README**: Write this up.
* **INSTALL**: Write this up.
* **Sphinx**: Continue documentation of all source in ``cloud_browser``.
  Currently at ``cloud_browser.cloud.base``.

Bugs
====

* If have a limit = 1 and have both a pseudo-directory and a dummy marker
  object with a name match and the browser is at the second object, clicking
  next doesn't work because the marker value is always the same and jumps to
  the second object again and again. -> VERIFY_FIX

Features
========

* **Browser**:

  * *Previous*: Add previous variable and lock to previous limit.

* **URL/View Choices**: Add different URLs, and maybe alternate views at the
  same time.

  * *Basic*: No AJAX, no admin.
  * *Admin*: Get anything available to admin, with admin decorators.
  * *AJAX*: Actually get AJAX.

* **Rackspace**:

  * *Container Listing*: Listing containers also uses ``limit`` and ``marker``
    and we should support this for large numbers of containers.

Test / Support
==============

* **Mem FS**: Write memory-based FS (Python-memory).
* **Unit Tests**: Add unit tests using fs/mem backing store.
* **Coverage**: Add coverage fabric targets.
