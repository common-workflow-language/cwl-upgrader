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
    version="1.2.3",
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
        "ruamel.yaml >= 0.16.0, < 0.17.22;python_version>='3.10'",
        "ruamel.yaml >= 0.15.98, < 0.17.22;python_version>='3.9'",
        "ruamel.yaml >= 0.15.78, < 0.17.22;python_version>='3.8'",
        "ruamel.yaml >= 0.15.71, < 0.17.22",
        "schema_salad",
    ],
    entry_points={"console_scripts": ["cwl-upgrader = cwlupgrader.main:main"]},
    python_requires=">=3.6, <4",
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    zip_safe=True,
    setup_requires=PYTEST_RUNNER,
    tests_require=["pytest < 7.2.0"],
    test_suite="tests",
)
