"""Fabric file."""
from __future__ import with_statement

import os
import re

from fabric.api import cd, abort, local, settings

###############################################################################
# Constants
###############################################################################
MOD = "cloud_browser"
PROJ = "cloud_browser_project"
PROJ_SETTINGS = ".".join((PROJ, "settings"))

DEV_DB_DIR = os.path.join(PROJ, "db")

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
DOC_UNDERSCORE_DIRS = (
    "sources",
    "static",
)

BUILD_DIRS = (
    "dist",
    "django_cloud_browser.egg-info"
)

SDIST_RST_FILES = (
    "INSTALL.rst",
    "README.rst",
)
SDIST_TXT_FILES = [os.path.splitext(x)[0] + ".txt" for x in SDIST_RST_FILES]


###############################################################################
# Build
###############################################################################
def clean():
    """Clean build files."""
    for build_dir in list(BUILD_DIRS) + [DOC_OUTPUT, DEV_DB_DIR]:
        local("rm -rf %s" % build_dir)


def sdist():
    """Package into distribution."""
    try:
        # Copy select *.rst files to *.txt for build.
        for rst_file, txt_file in zip(SDIST_RST_FILES, SDIST_TXT_FILES):
            local("cp %s %s" % (rst_file, txt_file))

        # Make build.
        local("python setup.py sdist", capture=False)
    finally:
        # Clean up temp *.txt files.
        for rst_file in SDIST_TXT_FILES:
            local("rm -f %s" % rst_file, capture=False)


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
def _parse_bool(value):
    """Convert ``string`` or ``bool`` to ``bool``."""
    if isinstance(value, bool):
        return value

    elif isinstance(value, basestring):
        if value == 'True':
            return True
        elif value == 'False':
            return False

    raise Exception("Value %s is not boolean." % value)


def docs(output=DOC_OUTPUT, proj_settings=PROJ_SETTINGS, github=False):
    """Generate API documentation (using Sphinx).

    :param output: Output directory.
    :param proj_settings: Django project settings to use.
    :param git: Convert output HTML to GitHub-friendly format?
    """
    local("export PYTHONPATH='' && "
          "export DJANGO_SETTINGS_MODULE=%s && "
          "sphinx-build -b html %s %s" % (proj_settings, DOC_INPUT, output),
          capture=False)

    if _parse_bool(github):
        print("Modifying Sphinx HTML for GitHub.")
        sphinx_to_github(output)


def sphinx_to_github(output=DOC_OUTPUT):
    """Convert Sphinx documents to a GitHub-friendly format.

    :param output: Output directory.
    """
    # Move directories.
    with cd(output):
        for dir_name in DOC_UNDERSCORE_DIRS:
            local("mv _%s %s" % (dir_name, dir_name), capture=False)

    def _get_html(dir_path):
        """Wrapper for getting HTML files."""
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_path.endswith(".html"):
                    yield file_path

    # Recursively replace links in HTML files using in-memory buffer.
    under_re = re.compile(
        r"(?P<first>(src|href)=[\"']([^\"']*[/]|))_(?P<dir>.*?/)")
    for file_path in _get_html(output):
        have_change = False
        lines = []

        # Store lines in memory and replace as appropriate.
        with open(file_path, 'rb') as ro_file:
            for line in ro_file:
                match = under_re.search(line)
                if match is not None:
                    have_change = True
                    line = under_re.sub(r"\g<first>\g<dir>", line)
                lines.append(line)

        # Re-open file as write and dump out modified lines.
        if have_change:
            print("Re-writing \"%s\"." % file_path)
            with open(file_path, 'wb') as w_file:
                w_file.writelines(lines)


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


def syncdb(proj_settings=PROJ_SETTINGS):
    """Run syncdb."""
    local("mkdir -p %s" % DEV_DB_DIR)
    _manage("syncdb", proj_settings=proj_settings)


def run_server(addr="127.0.0.1:8000", proj_settings=PROJ_SETTINGS):
    """Run Django dev. server."""
    _manage("runserver", addr, proj_settings)
