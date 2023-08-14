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
    version="2.0.0",
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
    package_data={"cwlupgrader.tests": ["../testdata/**/*.cwl"]},
    install_requires=[
        "setuptools",
        "ruamel.yaml >= 0.16.0, < 0.18",
        "schema_salad",
    ],
    entry_points={"console_scripts": ["cwl-upgrader = cwlupgrader.main:main"]},
    python_requires=">=3.8, <4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    zip_safe=True,
    setup_requires=PYTEST_RUNNER,
    tests_require=["pytest < 7.5.0"],
    test_suite="tests",
)
