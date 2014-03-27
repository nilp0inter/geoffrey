#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import os


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):

        #import here, cause outside the eggs aren't loaded
        import tox
        import coverage
        coverage.cmdline.main(argv=['erase'])
        errno = -1
        try:
            errno = tox.cmdline(self.test_args)
        except SystemExit as exitcode:
            errno = exitcode.code
        finally:
            if errno == 0:
                coverage.cmdline.main(argv=['combine'])
                coverage.cmdline.main(argv=['html'])

            # We don't use coverage.xml so remove it.
            os.system('rm -f coverage.xml')
            sys.exit(errno)

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
#          'websockets==2.0',
#          'pyinotify==0.9.4',
#          'enum34',
      ],
      packages=find_packages('src'),
      namespace_package=['geoffrey.plugins'],
      package_dir={'': 'src'},
      include_package_data=True,
      package_data={'geoffrey': ['web/*.*', 'web/assets/*.*']},
      entry_points={
          "console_scripts": ["geoffrey = geoffrey:main"]
      },
      tests_require=['tox', 'coverage'],
      cmdclass = {'test': Tox},
      )
