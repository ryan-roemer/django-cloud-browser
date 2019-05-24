Development setup
=================

You can set up the project and install development dependencies via:

.. sourcecode :: sh

    pip install -e .[test]

You can also run the CI locally via:

.. sourcecode :: sh

    fab check

Publishing a release
====================

There are two steps required to publish a new release:

1. Generate a Python distribution and upload it to PyPI.
2. Generate the documentation and upload it to Github Pages.

Both steps are automated via Travis CI and get run whenever
`a release is created on Github <https://help.github.com/en/articles/creating-releases>`_.
The tag version of the release will be used as the PyPI version identifier
and should follow the `semantic versioning <https://semver.org/>`_ convention
of :code:`major.minor.patch`.

Alternatively, the release steps can also be run locally via:

.. sourcecode :: sh

    # set credentials for PyPI
    export TWINE_USERNAME="..."
    export TWINE_PASSWORD="..."

    # set a personal access token with push access to the repo
    export GITHUB_TOKEN="..."

    # set the new version number
    export BUILD_VERSION="1.2.3"

    # run the release
    fab sdist publish_pypi docs publish_docs
