"""Fabric file."""

from fabric.api import cd, local

###############################################################################
# Constants
###############################################################################
MOD = "cloud_browser"
PROJ = "cloud_browser_project"
PROJ_SETTINGS = ".".join((PROJ, "settings"))

CHECK_INCLUDES = (
    "fabfile.py",
    MOD,
    PROJ,
)
PEP8_IGNORES = ('E225',)
PYLINT_CFG = "dev/pylint.cfg"


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
    local("pep8 %s %s" % (includes, ignores), capture=False)


def check():
    """Run all checkers."""
    pylint()
    pep8()


###############################################################################
# Django Targets
###############################################################################
def _manage(target, extra=''):
    """Generic wrapper for ``django-admin.py``."""
    local("export PYTHONPATH='' && "
          "export DJANGO_SETTINGS_MODULE='%s' && "
          "django-admin.py %s %s" %
          (PROJ_SETTINGS, target, extra),
          capture=False)


def run_server(addr="127.0.0.1:8000"):
    """Run Django dev. server."""
    _manage("runserver", addr)
    with cd(PROJ):
        local("python manage.py runserver --pythonpath='..' %s" % addr,
              capture=False)
