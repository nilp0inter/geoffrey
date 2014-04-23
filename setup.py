#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='geoffrey',
      version='0.0.1',
      description='Geoffrey is a continuous integration local server.',
      author='Roberto Abdelkader Martínez Pérez',
      author_email='robertomartinezp@gmail.com',
      url='http://github.com/nilp0inter/geoffrey',
      install_requires=[
          'aiohttp==0.6.4',
          'asyncio==0.4.1',
          'bottle==0.12.5',
          'Jinja2==2.7.2',
          'websockets==2.0',
          'enum34',
          'watchdog>=0.7.1',
      ],
      packages=find_packages('src'),
      namespace_package=['geoffrey.plugins'],
      package_dir={'': 'src'},
      include_package_data=True,
      package_data={'geoffrey': ['web/*.*', 'web/assets/*.*']},
      entry_points={
          "console_scripts": ["geoffrey = geoffrey:main"]
      },
      )
