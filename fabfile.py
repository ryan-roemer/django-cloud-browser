"""Fabric file."""
from __future__ import with_statement
from __future__ import print_function

import errno
import os
import shutil
import sys
from contextlib import contextmanager
from uuid import uuid4

from fabric.api import local


###############################################################################
# Constants
###############################################################################
ROOT_DIR = os.path.dirname(__file__)

MOD = "cloud_browser"
PROJ = "cloud_browser_project"
PROJ_SETTINGS = ".".join((PROJ, "settings"))

DEV_DB_DIR = os.path.join(PROJ, "db")

CHECK_INCLUDES = ("fabfile.py", "setup.py", MOD, PROJ)
PYLINT_CFG = os.path.join("dev", "pylint.cfg")
FLAKE8_CFG = os.path.join("dev", "flake8.cfg")

DOC_INPUT = "doc"
DOC_OUTPUT = "doc_html"
DOC_UNDERSCORE_DIRS = ("sources", "static")
DOC_BRANCH = "gh-pages"
GITHUB_USER = "ryan-roemer"
GITHUB_REPO = "django-cloud-browser"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

BUILD_DIRS = ("dist", "django_cloud_browser.egg-info")

SDIST_RST_FILES = ("INSTALL.rst", "README.rst", "CHANGES.rst")
SDIST_TXT_FILES = [os.path.splitext(x)[0] + ".txt" for x in SDIST_RST_FILES]

MANAGE = os.path.join(PROJ, "manage.py")


###############################################################################
# Build
###############################################################################
def clean():
    """Clean build files."""
    for build_dir in list(BUILD_DIRS) + [DOC_OUTPUT, DEV_DB_DIR]:
        try:
            shutil.rmtree(build_dir)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise


@contextmanager
def _dist_wrapper():
    """Add temporary distribution build files (and then clean up)."""
    try:
        # Copy select *.rst files to *.txt for build.
        for rst_file, txt_file in zip(SDIST_RST_FILES, SDIST_TXT_FILES):
            shutil.copy(rst_file, txt_file)

        # Perform action.
        yield
    finally:
        # Clean up temp *.txt files.
        for rst_file in SDIST_TXT_FILES:
            os.remove(rst_file)


def sdist():
    """Package into distribution."""
    with _dist_wrapper():
        local("python setup.py sdist", capture=False)


def register():
    """Register and prep user for PyPi upload.

    .. note:: May need to tweak ~/.pypirc file per issue:
        http://stackoverflow.com/questions/1569315
    """
    with _dist_wrapper():
        local("python setup.py register", capture=False)


def upload():
    """Upload package."""
    with _dist_wrapper():
        local("python setup.py sdist", capture=False)
        local("twine upload dist/*", capture=False)


###############################################################################
# Quality
###############################################################################
def pylint(rcfile=PYLINT_CFG):
    """Run pylint style checker.

    :param rcfile: PyLint configuration file.
    """
    # Have a spurious DeprecationWarning in pylint.
    local("pylint --rcfile=%s %s" % (rcfile, " ".join(CHECK_INCLUDES)), capture=False)


def flake8(rcfile=FLAKE8_CFG):
    """Run flake8 style checker.

    :param rcfile: Flake8 configuration file.
    """
    local("flake8 --config=%s %s" % (rcfile, " ".join(CHECK_INCLUDES)), capture=False)


def black():
    """Run black style checker."""
    if sys.version_info.major > 2:
        local("black --check %s" % (" ".join(CHECK_INCLUDES)), capture=False)


def check():
    """Run all checkers."""
    flake8()
    black()
    pylint()


###############################################################################
# Documentation
###############################################################################
def _touch(file_path):
    with open(file_path, "wb") as fobj:
        fobj.write(b"")

    return fobj.name


def docs(output=DOC_OUTPUT, proj_settings=PROJ_SETTINGS):
    """Generate API documentation (using Sphinx).

    :param output: Output directory.
    :param proj_settings: Django project settings to use.
    """

    os.environ["PYTHONPATH"] = ROOT_DIR
    os.environ["DJANGO_SETTINGS_MODULE"] = proj_settings

    local("sphinx-build -b html %s %s" % (DOC_INPUT, output), capture=False)


def publish_docs(
    from_folder=DOC_OUTPUT,
    to_branch=DOC_BRANCH,
    github_token=GITHUB_TOKEN,
    github_user=GITHUB_USER,
    github_repo=GITHUB_REPO,
):
    _touch(os.path.join(DOC_OUTPUT, ".nojekyll"))

    temp_remote = "publish-%s" % uuid4()
    local(
        "git remote add %s https://%s@github.com/%s/%s"
        % (temp_remote, github_token, github_user, github_repo)
    )
    local(
        "gh-pages --dotfiles --dist %s --branch %s --remote %s"
        % (from_folder, to_branch, temp_remote)
    )
    local("git remote rm %s" % temp_remote)


###############################################################################
# Django Targets
###############################################################################
def _manage(target, extra=""):
    """Generic wrapper for ``manage.py``."""
    os.environ["PYTHONPATH"] = ROOT_DIR

    local("python %s %s %s" % (MANAGE, target, extra), capture=False)


def syncdb():
    """Run syncdb."""
    try:
        os.makedirs(DEV_DB_DIR)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise

    _manage("syncdb")


def run_server(addr="127.0.0.1:8000"):
    """Run Django dev. server."""
    _manage("runserver", addr)
