======================
 Django Cloud Browser
======================
:Info: A Django application browser for cloud (S3, Cloud Files) datastores.
:Author: Ryan Roemer (http://github.com/ryan-roemer)
:Build: |travis| |github| |style|
:Version: |version| |dockerhub|

Cloud Browser is a simple web-based object browser for cloud-based blob
datastores. Just add as an application to a Django project, add some settings,
and you'll be able to browse cloud containers and implied subdirectories, as
well as view / download objects.

Currently supported backend datastores include:

* Local file system for testing.
* `Amazon S3`_
* `Azure Blob Storage`_
* `Google Cloud Storage`_
* `OpenStack Swift`_
* `And many more`_

.. _`Apache Libcloud`: https://libcloud.readthedocs.io/en/latest/storage/index.html
.. _`Amazon S3`: http://aws.amazon.com/s3/
.. _`Azure Blob Storage`: https://azure.microsoft.com/en-us/services/storage/blobs/
.. _`Google Cloud Storage`: https://cloud.google.com/storage/
.. _`OpenStack Swift`: https://www.swiftstack.com/product/open-source/openstack-swift
.. _`And many more`: https://libcloud.readthedocs.io/en/latest/storage/supported_providers.html

Be sure to check out the following project resources:

* Documentation_.
* `GitHub page`_.

.. _Documentation: http://ryan-roemer.github.com/django-cloud-browser/
.. _`GitHub page`: https://github.com/ryan-roemer/django-cloud-browser/
.. toc

Access Controls
===============

Cloud Browser also has a very rudimentary set of access controls (presently
white and black lists), so that you can expose a subset of cloud objects
to a set of less-then-fully trusted users for read-only access without having
to pass around the full cloud API account and secret key.

Nested File Browsing
====================

One of the underlying motivations for this project is the current control
panel for Rackspace Cloud Files that only allows listing of the flat object
namespace within a container, without any nested hierarchy. When you get up to
5 million or so objects, it can be tedious / impracticable to search through
results, even if you have carefully added delimiters (e.g., slashes) to your
cloud objects names.

Accordingly, Cloud Browser correctly handles "implicit" or "pseudo" directories
in the underlying flat namespace of cloud blob names (e.g., divides up an
object called "long/path/with/slashes/to/foo.txt"), and allows viewing into the
artificially nested hierarchy. Cloud object results are paged, and subsequent
pages can be viewed at arbitrary object-per-page and starting points.
Conveniently, URL paths can be inputted and linked to a starting point within
a long list of results.

.. |travis| image:: https://travis-ci.org/ryan-roemer/django-cloud-browser.svg
   :target: https://travis-ci.org/ryan-roemer/django-cloud-browser

.. |github| image:: https://github.com/ryan-roemer/django-cloud-browser/workflows/CI/badge.svg
   :target: https://github.com/ryan-roemer/django-cloud-browser/actions?query=workflow%3ACI

.. |style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black

.. |version| image:: https://img.shields.io/pypi/v/django-cloud-browser.svg
   :target: https://pypi.org/project/django-cloud-browser/

.. |dockerhub| image:: https://images.microbadger.com/badges/version/cwolff/django-cloud-browser.svg
   :target: https://hub.docker.com/r/cwolff/django-cloud-browser/tags
