"""Cloud browser package."""

from setuptools import setup, find_packages

from cloud_browser import __version__

# Base packages.
MOD_NAME = "cloud_browser"
PKGS = [x for x in find_packages() if x.split('.')[0] == MOD_NAME]

setup(
    name="django-cloud-browser",
    version=__version__,
    description="Django Cloud Browser application.",
    long_description="Django browser for cloud datastores (Rackspace).",
    url="https://github.com/ryan-roemer/django-cloud-browser",

    author="Ryan Roemer",
    author_email="ryan@loose-bits.com",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
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
