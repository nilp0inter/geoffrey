#!/usr/bin/env python
"""
Geoffrey setup file.
"""
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
