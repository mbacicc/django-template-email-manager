#!/usr/bin/env python

from os.path import exists
import os
from setuptools import setup, find_packages
import re

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('template_email_manager')
with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='django-template-email-manager',
    version=version,
    author='mbacicc',
    author_email='mbacicc@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/mbacicc/django-template-email-manager',
    license='MIT',
    description='A small useful app to manage email queues with run-time db-stored customizable templates from any django project',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'django',
    ],
    python_requires='>=3.6',
)
