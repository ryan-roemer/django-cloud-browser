"""Fabric file."""

from fabric.api import cd, local

###############################################################################
# Constants
###############################################################################
MOD = "cloud_browser"
PROJ = "cloud_browser_project"

CHECK_INCLUDES = (
    "fabfile.py",
    MOD,
    PROJ,
)
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
    local("pep8 -r %s" % " ".join(CHECK_INCLUDES), capture=False)


###############################################################################
# Django Targets
###############################################################################
def run_server(addr="127.0.0.1:8000"):
    """Run Django dev. server."""
    with cd(PROJ):
        local("python manage.py runserver --pythonpath='..' %s" % addr,
              capture=False)
