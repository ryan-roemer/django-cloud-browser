====================
 Future / Task List
====================

Current
=======

* Add license.
* Finish README.rst, INSTALL.rst.
* Github push.
* Github documentation push.

Packaging
=========

* PyPi registration.
* Development pip requirements file.

Features
========

* **Configuration**:

  * *Boto Config*: Allow using ``.boto`` file to provide settings.
  * *Whitelist*: Allow a combined whitelist/blacklist user callable.

* **Browser**:

  * *Previous*: Add previous variable and lock to previous limit.
  * *Sort*: See if ``boto`` / ``cloudfiles`` both support sorted results.

* **URL/View AJAX Options**: Enable AJAX, maybe with separate URLs.

* **Rackspace**:

  * *Container Listing*: Listing containers also uses ``limit`` and ``marker``
    and we should support this for large numbers of containers.

Test / Support
==============

* **Mem FS**: Write memory-based FS (Python-memory).
* **Unit Tests**: Add unit tests using fs/mem backing store.
* **Coverage**: Add coverage fabric targets.
