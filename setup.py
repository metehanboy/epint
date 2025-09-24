#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from epint import __version__
except ImportError:
    __version__ = "0.1.0"


def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "EPINT - EPIAS API Integration Package"


def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [
                line.strip() for line in fh if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return ["requests>=2.31.0", "urllib3>=2.0.0", "pyyaml>=6.0.1"]


setup(
    name="epint",
    version=__version__,
    author="EPINT Team",
    author_email="epint@example.com",
    description="EPIAS API Integration Package for Turkish Energy Market",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/epint/epint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
