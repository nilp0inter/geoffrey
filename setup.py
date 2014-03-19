#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='geoffrey',
      version='0.0.1',
      description='Geoffrey is a continuous integration local server.',
      author='Roberto Abdelkader Martínez Pérez',
      author_email='robertomartinezp@gmail.com',
      url='http://github.com/nilp0inter/geoffrey',
      install_requires=[
          'asyncio==0.4.1',
          'websockets==2.0',
          'pyinotify==0.9.4',
          'enum34',
          'Jinja2==2.7.2',
          'bottle==0.12.5',
      ],
      packages=find_packages('src'),
      namespace_package=['geoffrey.plugins'],
      package_dir={'': 'src'},
      include_package_data=True,
      package_data={'geoffrey': ['web/*.*', 'web/assets/*.*']},
      entry_points={
          "console_scripts": ["geoffrey = geoffrey.server:main"]
      },
      )
