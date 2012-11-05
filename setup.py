"""Cloud browser package."""
from __future__ import with_statement
import os
from setuptools import setup, find_packages

from cloud_browser import __version__

###############################################################################
# Environment and Packages.
###############################################################################
# Don't copy Mac OS X resource forks on tar/gzip.
os.environ['COPYFILE_DISABLE'] = "true"

# Packages.
MOD_NAME = "cloud_browser"
PKGS = [x for x in find_packages() if x.split('.')[0] == MOD_NAME]


###############################################################################
# Helpers.
###############################################################################
def read_file(name):
    """Read file name (without extension) to string."""
    cur_path = os.path.dirname(__file__)
    exts = ('txt', 'rst')
    for ext in exts:
        path = os.path.join(cur_path, '.'.join((name, ext)))
        if os.path.exists(path):
            with open(path, 'rb') as file_obj:
                return file_obj.read()

    return ''


###############################################################################
# Setup.
###############################################################################
setup(
    name="django-cloud-browser",
    version=__version__,
    description="Django Cloud Browser application.",
    long_description=read_file("README"),
    url="http://ryan-roemer.github.com/django-cloud-browser",

    author="Ryan Roemer",
    author_email="ryan@loose-bits.com",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],

    install_requires=[
        "distribute",
    ],

    packages=PKGS,
    include_package_data=True,
)
