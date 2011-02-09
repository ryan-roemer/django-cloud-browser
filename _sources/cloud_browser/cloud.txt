=====================================================
 ``cloud_browser.cloud`` - Cloud / Datastore Support
=====================================================

.. automodule:: cloud_browser.cloud

``cloud_browser.cloud.config`` - Configuration
==============================================
.. automodule:: cloud_browser.cloud.config
   :members:

``cloud_browser.cloud.config`` - Errors
=======================================
.. automodule:: cloud_browser.cloud.errors
   :members:

Datastores
==========
Cloud Browser is written with a pluggable backend datastore model in mind.
Currently, there are datastore implementations for a basic filesystem and
cloud (Rackspace, Amazon) backing stores. Other cloud stores shouldn't be too
hard to port over to this app, as Rackspace has probably the most little
extra "gotcha's" in listing objects using implied / pseudo- directories.

``cloud_browser.cloud.base`` - Abstract Base
--------------------------------------------
.. automodule:: cloud_browser.cloud.base
   :members:

``cloud_browser.cloud.fs`` - Filesystem Datastore
-------------------------------------------------
.. automodule:: cloud_browser.cloud.fs
   :members:

``cloud_browser.cloud.aws`` - Amazon Web Services S3 Datastore
--------------------------------------------------------------
.. automodule:: cloud_browser.cloud.aws
   :members:

``cloud_browser.cloud.rackspace`` - Rackspace Cloud Files Datastore
-------------------------------------------------------------------
.. automodule:: cloud_browser.cloud.rackspace
   :members:


