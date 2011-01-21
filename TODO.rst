==================
 TODO / Task List
==================

Logistics
=========

* **README**: Write this up.
* **Sphinx**: Continue documentation of all source in ``cloud_browser``.

Bugs
====

* If have a limit = 1 and have both a pseudo-directory and a dummy marker
  object with a name match and the browser is at the second object, clicking
  next doesn't work because the marker value is always the same and jumps to
  the second object again and again.

Features
========

* **Browser**:

  * *Previous*: Add previous variable and lock to previous limit.

* **URL/View Choices**: Add different URLs, and maybe alternate views at the
  same time.

  * *Basic*: No AJAX, no admin.
  * *Admin*: Get anything available to admin, with admin decorators.
  * *AJAX*: Actually get AJAX.

Test / Support
==============

* **Mem FS**: Write memory-based FS (Python-memory).
* **Unit Tests**: Add unit tests using fs/mem backing store.
