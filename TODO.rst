====================
 Future / Task List
====================

Current
=======
* **Google Storage**: Parse up pseudo-directories differently and handle:

  * The extra ``_$folder$`` semantics.
  * Extra subdirectory 0 byte object for each implied directory. (Might be
    added by CyberDuck).

* Vendor notes.

Packaging
=========
* Development pip requirements file.

Design / UI
===========
* **CSS Rework**: Styles and appearance need vast improvements. Hopefully
  we'll get some help with this soon.

Features
========
* **Admin URLs/Templates**:

  * Write up how to configure this (with admin authorization).
  * Figure out a hack to get link to show up on "/admin/" page.
  * Use JS or have option to hide containers list (maybe in any context).

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
