==================
 TODO / Task List
==================

Current
=======

* Add license.
* Finish README.rst, INSTALL.rst.

Documentation
=============

* **README**: Write this up.
* **INSTALL**: Write this up.
* **Sphinx**: Continue documentation of all source in ``cloud_browser``.
  Currently at ``cloud_browser.cloud.base``.

Features
========

* **Configuration**:

  * *Datastore Type*: Actually have a parameter for this (rather than order).
  * *Boto Config*: Allow using ``.boto`` file to provide settings.
  * *Whitelist*: Allow a combined whitelist/blacklist user callable.

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
