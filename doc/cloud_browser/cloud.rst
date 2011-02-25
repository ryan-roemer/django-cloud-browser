===========================
 Cloud / Datastore Support
===========================

.. automodule:: cloud_browser.cloud

Configuration
=============
.. automodule:: cloud_browser.cloud.config
   :members:

Errors
======
.. automodule:: cloud_browser.cloud.errors
   :members:

Datastores
==========
Cloud Browser is written with a pluggable backend datastore model in mind.
Currently, there are datastore implementations for a basic filesystem and
cloud (Rackspace, Amazon) backing stores. Other cloud stores shouldn't be too
hard to port over to this app, as Rackspace has probably the most little
extra "gotcha's" in listing objects using implied / pseudo- directories.

Abstract Base Class
-------------------
.. automodule:: cloud_browser.cloud.base
   :members:

Filesystem Datastore
--------------------
.. automodule:: cloud_browser.cloud.fs
   :members:

Amazon Web Services S3 Datastore
--------------------------------
.. automodule:: cloud_browser.cloud.aws
   :members:

Rackspace Cloud Files Datastore
-------------------------------
.. automodule:: cloud_browser.cloud.rackspace
   :members:


