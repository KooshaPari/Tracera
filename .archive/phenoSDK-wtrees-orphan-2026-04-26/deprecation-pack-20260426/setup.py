#!/usr/bin/env python3
"""
Setup script for pheno-sdk
Explicitly defines packages to avoid flat-layout discovery issues
"""

from setuptools import setup

setup(
    name="pheno-sdk",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=["pheno"],
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "pheno": ["py.typed"],
    },
)
