#!/usr/bin/env python
"""
Geoffrey setup file.

"""
#pylint: disable=I0011, W0122
import io
import os
import setuptools

BASE_DIR = os.path.dirname(__file__)
PKG_DIR = os.path.join(BASE_DIR, "src", "geoffrey")

META = {}
with io.open(os.path.join(PKG_DIR, "__meta__.py"), 'rb') as f:
    exec(f.read(), META)

with io.open(os.path.join(BASE_DIR, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

extras_require = {}

extras_require["local"] = [
    "geoffrey-filesystem",
    "geoffrey-filecontent"]

extras_require["python"] = [
    "geoffrey-cheesecake",
    "geoffrey-clonedigger",
    "geoffrey-csslint",
    "geoffrey-filecontent",
    "geoffrey-filesystem",
    "geoffrey-jshint",
    "geoffrey-pyflakes",
    "geoffrey-pylint",
    "geoffrey-pyreverse",
    "geoffrey-pytest",
    "geoffrey-radon",
    "geoffrey-snakefood"]

extras_require["java"] = [
    "geoffrey-clonedigger"]

extras_require["misc"] = [
    "geoffrey-todo"]

extras_require["all"] = [p for p in (v for v in extras_require.values())]

setuptools.setup(
    name=META["__packagename__"],
    version=META["__version__"],
    description=META["__summary__"],
    long_description=LONG_DESCRIPTION,
    classifiers=[
    ],
    keywords=META["__keywords__"],
    author=META["__author__"],
    author_email=META["__email__"],
    maintainer=META["__maintainer__"],
    maintainer_email=META["__maintainer_email__"],
    license=META["__license__"],
    url=META["__url__"],
    install_requires=[
        'aiohttp==0.6.4',
        'bottle==0.12.5',
        'Jinja2==2.7.2',
        'websockets==2.1',
    ],
    entry_points={
        "console_scripts": ["geoffrey = geoffrey.main:main"]
    },
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require=extras_require
)
