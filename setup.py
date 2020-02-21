#!/usr/bin/env python
from setuptools import find_packages, setup

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()

config = configparser.ConfigParser()
config.read("setup.cfg")

setup(
    name="stack_exchange_graph_data",
    version=config.get("src", "version"),
    license="MIT",
    description="Converts Stack Exchange data dumps to Gephi importable spreadsheets",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Peilonrayz",
    author_email="peilonrayz@gmail.com",
    url="https://peilonrayz.github.io/stack_exchange_graph_data",
    project_urls={
        "Bug Tracker": "https://github.com/Peilonrayz/stack_exchange_graph_data/issues",
        "Documentation": "https://peilonrayz.github.io/stack_exchange_graph_data",
        "Source Code": "https://github.com/Peilonrayz/stack_exchange_graph_data",
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "docutils",
        "recommonmark",
        "sphinx",
        "beautifulsoup4",
        "defusedxml",
        "requests",
        "pylzma",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="stackexchange sede",
    entry_points={"console_scripts": ["segd=stack_exchange_graph_data.__main__:main"]},
)
