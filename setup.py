#!/usr/bin/env python
from io import open
import os
import setuptools

BASE_DIR = os.path.dirname(__file__)
PKG_DIR = os.path.join(BASE_DIR, "src", "geoffrey")

meta = {}
with open(os.path.join(PKG_DIR, "__meta__.py"), 'rb') as f:
    exec(f.read(), meta)

with open(os.path.join(BASE_DIR, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name=meta["__packagename__"],
    version=meta["__version__"],
    description=meta["__summary__"],
    long_description=long_description,
    classifiers=[
    ],
    keywords=meta["__keywords__"],
    author=meta["__author__"],
    author_email=meta["__email__"],
    maintainer=meta["__maintainer__"],
    maintainer_email=meta["__maintainer_email__"],
    license=meta["__license__"],
    url=meta["__url__"],
    install_requires=[
        'aiohttp==0.6.4',
        'asyncio==0.4.1',
        'bottle==0.12.5',
        'Jinja2==2.7.2',
        'websockets==2.0',
        'enum34',
        'watchdog>=0.7.1',
        'filemagic==1.6',
    ],
    entry_points={
        "console_scripts": ["geoffrey = geoffrey.main:main"]
    },

    packages=['geoffrey', 'geoffrey.plugins'],
    namespace_packages=['geoffrey', 'geoffrey.plugins'],
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'geoffrey': ['web/*.*', 'web/assets/*.*', 'plugins/*/*']},
)
