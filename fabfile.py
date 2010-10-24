"""Fabric file."""

from fabric.api import cd, local

PROJ = "cloud_browser_project"

def run_server(addr="127.0.0.1:8000"):
  """Run Django dev. server."""
  with cd(PROJ):
    local(
      "python manage.py runserver --pythonpath='..' %s" % addr, capture=False)
