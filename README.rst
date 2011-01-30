======================
 Django Cloud Browser
======================
:Info: A Django application browser for cloud (S3, Cloud Files) datastores.
:Author: Ryan Roemer (http://github.com/ryan-roemer)

Cloud Browser is a simple web-based object browser for cloud-based blob
datastores. Just add as an application to a Django project, add some settings,
and you'll be able to view and download cloud containers and objects, with
a very rudimentary amount of access control.

Currently supported backend datastores include:

* `Amazon S3`_.
* `Rackspace Cloud Files`_.
* Local filesytem.

.. _`Amazon S3`: http://aws.amazon.com/s3/
.. _`Rackspace Cloud Files`:
  http://www.rackspacecloud.com/cloud_hosting_products/files/

One of the underlying motivations for this project is the current control
panel for Rackspace Cloud Files that only allows listing of the flat object
namespace within a container, without any nested hierarchy. When you get up to
5 million or so objects, it can be tedious / impractible to search through
results, even if you have carefully added delimiters (e.g., slashes) to your
cloud objects names.

Accordingly, Cloud Browser correctly handles "implicit" or "pseudo" directories
in the underlying flat namespace of cloud blob names (e.g., divides up an
object called "long/path/with/slashes/to/foo.txt"), and allows viewing into the
artificially nested hierarchy. Cloud object results are paged, and subsequent
pages can be viewed at arbitrary object-per-page and starting points.
Conveniently, URL paths can be inputted and linked to a starting point within
a long list of results.
