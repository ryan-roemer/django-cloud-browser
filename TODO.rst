====================
 Future / Task List
====================

Current
=======
* Vendor notes.

Packaging
=========
* Development pip requirements file.

Design / UI
===========
* **CSS Rework**: Styles and appearance need vast improvements. Hopefully
  we'll get some help with this soon.

API
===
* **Browser**:

  * *Previous*: Add previous variable and lock to previous limit.
  * *Sort*: See if ``boto`` / ``cloudfiles`` both support sorted results.

* **Metadata**: Display.

* **Modify**: Long-term project.

  * *Upload Object*:
  * *Delete Object*:
  * *Create Bucket*:
  * *Delete Bucket*:
  * *Create Pseudo-Directory*: (Maybe)
  * *Delete Pseudo-Directory*: (Maybe)
  * *Edit Object Metadata*:

Features
========
* **Admin URLs/Templates**:

  * Write up how to configure this (with admin authorization).
  * Figure out a hack to get link to show up on "/admin/" page.
  * Use JS or have option to hide containers list (maybe in any context).

* **Configuration**:

  * *Boto Config*: Allow using ``.boto`` file to provide settings.
  * *Whitelist*: Allow a combined whitelist/blacklist user callable.

* **URL/View AJAX Options**: Enable AJAX, maybe with separate URLs.

* **Rackspace**:

  * *Container Listing*: Listing containers also uses ``limit`` and ``marker``
    and we should support this for large numbers of containers.

Test / Support
==============
* **Mem FS**: Write memory-based FS (Python-memory).
* **Unit Tests**: Add unit tests using fs/mem backing store.
* **Coverage**: Add coverage fabric targets.
