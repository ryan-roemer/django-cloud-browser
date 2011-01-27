"""Fabric file."""
from __future__ import with_statement

from fabric.api import abort, local, settings

###############################################################################
# Constants
###############################################################################
MOD = "cloud_browser"
PROJ = "cloud_browser_project"
PROJ_SETTINGS = ".".join((PROJ, "settings"))

CHECK_INCLUDES = (
    "fabfile.py",
    "setup.py",
    MOD,
    PROJ,
)
PEP8_IGNORES = ('E225',)
PYLINT_CFG = "dev/pylint.cfg"

DOC_INPUT = "doc"
DOC_OUTPUT = "doc_html"

BUILD_DIRS = ("dist", "django_cloud_browser.egg-info")


###############################################################################
# Build
###############################################################################
def clean():
    """Clean build files."""
    local("rm -rf %s" % DOC_OUTPUT)
    for build_dir in BUILD_DIRS:
        local("rm -rf %s" % build_dir)


def sdist():
    """Package into distribution."""
    local("python setup.py sdist", capture=False)


###############################################################################
# Quality
###############################################################################
def pylint(rcfile=PYLINT_CFG):
    """Run pylint style checker.

    :param rcfile: PyLint configuration file.
    """
    # Have a spurious DeprecationWarning in pylint.
    local(
        "python -W ignore::DeprecationWarning `which pylint` --rcfile=%s %s" %
        (rcfile, " ".join(CHECK_INCLUDES)), capture=False)


def pep8():
    """Run pep8 style checker."""
    includes = "-r %s" % " ".join(CHECK_INCLUDES)
    ignores = "--ignore=%s" % ",".join(PEP8_IGNORES) if PEP8_IGNORES else ''
    with settings(warn_only=True):
        results = local("pep8 %s %s" % (includes, ignores), capture=True)
    errors = results.strip() if results else None
    if errors:
        print(errors)
        abort("PEP8 failed.")


def check():
    """Run all checkers."""
    pep8()
    pylint()


###############################################################################
# Documentation
###############################################################################
def docs(output=DOC_OUTPUT, proj_settings=PROJ_SETTINGS):
    """Generate API documentation (using Sphinx)."""
    local("export DJANGO_SETTINGS_MODULE=%s && "
          "sphinx-build -b html %s %s" % (proj_settings, DOC_INPUT, output),
          capture=False)


###############################################################################
# Django Targets
###############################################################################
def _manage(target, extra='', proj_settings=PROJ_SETTINGS):
    """Generic wrapper for ``django-admin.py``."""
    local("export PYTHONPATH='' && "
          "export DJANGO_SETTINGS_MODULE='%s' && "
          "django-admin.py %s %s" %
          (proj_settings, target, extra),
          capture=False)


def run_server(addr="127.0.0.1:8000", proj_settings=PROJ_SETTINGS):
    """Run Django dev. server."""
    _manage("runserver", addr, proj_settings)
