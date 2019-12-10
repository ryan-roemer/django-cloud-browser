"""Fabric file."""
from __future__ import print_function, with_statement

import errno
import os
import shutil
from contextlib import contextmanager
from fileinput import FileInput
from sys import version_info
from uuid import uuid4

from invoke import task

###############################################################################
# Constants
###############################################################################
ROOT_DIR = os.path.dirname(__file__)

MOD = "cloud_browser"
PROJ = "cloud_browser_project"
PROJ_SETTINGS = ".".join((PROJ, "settings"))

DEV_DB_DIR = os.path.join(PROJ, "db")

CHECK_INCLUDES = ("tasks.py", "setup.py", MOD, PROJ)
PYLINT_CFG = os.path.join("dev", "pylint.cfg")
FLAKE8_CFG = os.path.join("dev", "flake8.cfg")
ISORT_CFG = os.path.join("dev", ".isort.cfg")

DOC_INPUT = "doc"
DOC_OUTPUT = "doc_html"
DOC_UNDERSCORE_DIRS = ("sources", "static")
DOC_BRANCH = "gh-pages"
GITHUB_USER = "ryan-roemer"
GITHUB_REPO = "django-cloud-browser"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

DOCKER_USER = "cwolff"
DOCKER_IMAGE = "django-cloud-browser"
DOCKER_PASSWORD = os.environ.get("DOCKER_PASSWORD")

BUILD_VERSION = os.environ.get("BUILD_VERSION")
BUILD_DIRS = ("dist", "django_cloud_browser.egg-info")

SDIST_RST_FILES = ("INSTALL.rst", "README.rst", "CHANGES.rst")
SDIST_TXT_FILES = [os.path.splitext(x)[0] + ".txt" for x in SDIST_RST_FILES]

MANAGE = os.path.join(PROJ, "manage.py")

try:
    SERVER_ADDRESS = "%s:%s" % (os.environ["HOST"], os.environ["PORT"])
except KeyError:
    SERVER_ADDRESS = "127.0.0.1:8000"


###############################################################################
# Build
###############################################################################
@task
def clean(_):
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


@contextmanager
def _update_version(context, version):
    if not version:
        yield
        return

    major, minor, patch = version.strip().split(".")
    version_file = os.path.join(ROOT_DIR, MOD, "__init__.py")
    fobj = FileInput(version_file, inplace=True)
    try:
        for line in fobj:
            if line.startswith("VERSION = ("):
                print("VERSION = (%s, %s, %s)" % (major, minor, patch))
            else:
                print(line)
    finally:
        fobj.close()

    yield

    context.run("git checkout %s" % version_file)


@task
def sdist(context, version=BUILD_VERSION):
    """Package into distribution."""
    with _update_version(context, version), _dist_wrapper():
        context.run("python setup.py sdist")


@task
def register(context):
    """Register and prep user for PyPi upload.

    .. note:: May need to tweak ~/.pypirc file per issue:
        http://stackoverflow.com/questions/1569315
    """
    with _dist_wrapper():
        context.run("python setup.py register")


@task
def publish_pypi(context):
    """Upload package."""
    context.run("twine upload dist/*")


###############################################################################
# Quality
###############################################################################
@task
def pylint(context, rcfile=PYLINT_CFG):
    """Run pylint style checker."""
    # Have a spurious DeprecationWarning in pylint.
    context.run("pylint --rcfile=%s %s" % (rcfile, " ".join(CHECK_INCLUDES)))


@task
def flake8(context, rcfile=FLAKE8_CFG):
    """Run flake8 style checker."""
    context.run("flake8 --config=%s %s" % (rcfile, " ".join(CHECK_INCLUDES)))


@task
def isort(context, rcfile=ISORT_CFG):
    """Run isort style checker."""
    # use dirname until https://github.com/timothycrosley/isort/issues/710 is resolved
    rcfile = os.path.dirname(rcfile)

    context.run(
        "isort --recursive --check-only --settings-path=%s %s"
        % (rcfile, " ".join(CHECK_INCLUDES))
    )


@task
def black(context):
    """Run black style checker."""
    if version_info >= (3, 6, 0):
        context.run("black --check %s" % (" ".join(CHECK_INCLUDES)))


@task(flake8, isort, black, pylint)
def check(_):
    """Run all checkers."""
    pass


###############################################################################
# Documentation
###############################################################################
def _touch(file_path):
    with open(file_path, "wb") as fobj:
        fobj.write(b"")

    return fobj.name


@task
def docs(
    context, output=DOC_OUTPUT, proj_settings=PROJ_SETTINGS, version=BUILD_VERSION
):
    """Generate API documentation (using Sphinx)."""
    os.environ["PYTHONPATH"] = ROOT_DIR
    os.environ["DJANGO_SETTINGS_MODULE"] = proj_settings

    with _update_version(context, version):
        context.run("sphinx-build -b html %s %s" % (DOC_INPUT, output))


@task
def publish_docs(
    context,
    from_folder=DOC_OUTPUT,
    to_branch=DOC_BRANCH,
    github_token=GITHUB_TOKEN,
    github_user=GITHUB_USER,
    github_repo=GITHUB_REPO,
):
    _touch(os.path.join(DOC_OUTPUT, ".nojekyll"))

    temp_remote = "publish-%s" % uuid4()
    context.run(
        "git remote add %s https://%s@github.com/%s/%s"
        % (temp_remote, github_token, github_user, github_repo)
    )
    context.run(
        "gh-pages --dotfiles --dist %s --branch %s --remote %s"
        % (from_folder, to_branch, temp_remote)
    )
    context.run("git remote rm %s" % temp_remote)


@task
def publish_docker(
    context, user=DOCKER_USER, image=DOCKER_IMAGE, version=BUILD_VERSION
):
    context.run("docker login -u %s -p %s" % (user, DOCKER_PASSWORD))
    for tag in version, "latest":
        image_name = "%s/%s:%s" % (user, image, tag)
        context.run("docker build -t %s ." % image_name)
        context.run("docker push %s" % image_name)


###############################################################################
# Django Targets
###############################################################################
def _manage(context, target, extra=""):
    """Generic wrapper for ``manage.py``."""
    os.environ["PYTHONPATH"] = ROOT_DIR
    os.environ["PYTHONUNBUFFERED"] = "1"

    context.run("python %s %s %s" % (MANAGE, target, extra))


@task
def syncdb(context):
    """Run syncdb."""
    try:
        os.makedirs(DEV_DB_DIR)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise

    _manage(context, "syncdb", "--noinput")


@task
def run_server(context, addr=SERVER_ADDRESS):
    """Run Django dev. server."""
    _manage(context, "runserver", addr)
