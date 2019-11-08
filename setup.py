#!/usr/bin/env python

import os
import sys

from setuptools import setup

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, "README.rst")

NEEDS_PYTEST = {"pytest", "test", "ptr"}.intersection(sys.argv)
PYTEST_RUNNER = ["pytest-runner", "pytest-cov"] if NEEDS_PYTEST else []

setup(
    name="cwl-upgrader",
    version="0.5",
    description="Common Workflow Language standalone document upgrader",
    long_description=open(README).read(),
    author="Common Workflow Language contributors",
    author_email="common-workflow-language@googlegroups.com",
    url="https://github.com/common-workflow-language/cwl-upgrader",
    download_url="https://github.com/common-workflow-language/cwl-upgrader",
    license="Apache 2.0",
    packages=["cwlupgrader", "cwlupgrader.tests"],
    include_package_data=True,
    package_dir={"cwlupgrader.tests": "tests"},
    package_data={"cwlupgrader.tests": ["*.cwl"]},
    install_requires=["setuptools", "ruamel.yaml>=0.16,<0.17", "typing"],
    entry_points={"console_scripts": ["cwl-upgrader = cwlupgrader.main:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    zip_safe=True,
    setup_requires=[] + PYTEST_RUNNER,
    tests_require=["pytest < 5.3.0"],
    test_suite="tests",
)
