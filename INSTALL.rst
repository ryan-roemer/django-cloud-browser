==============
 Installation
==============

Installing the Cloud Browser package is straightforward::

    pip install django-cloud-browser

or::

    easy_install django-cloud-browser

Software Requirements
=====================

Cloud Browser uses conditional imports to only actually require other libraries
that are used in the active configuration. Loosely speaking, for deployment,
only the following is actually needed:

* Python 2.5+
* `Django <http://www.djangoproject.com/>`_

The application relies on third party open source libraries to actually
communicate with cloud datastores, so for each cloud datastore you need the
corresponding library below:

* Amazon S3: `boto <http://code.google.com/p/boto/>`_
* Rackspace Cloud Files:
  `cloudfiles <https://github.com/rackspace/python-cloudfiles>`_
  (version 1.7.4+ is required).

Configuration
=============
TODO

Static Media
============
TODO

Examples
========
The source contains an `example project`_ that is configures and serves up the
Cloud Browser application, and little more. It is a good starting point if you
are having difficulties getting things going.

.. _`example project`: https://github.com/ryan-roemer/django-cloud-browser/
  blob/master/cloud_browser_project
