Geoffrey
========


Geoffrey is a real time continuous integration server.

.. image:: https://raw.githubusercontent.com/nilp0inter/geoffrey/develop/src/geoffrey/web/assets/geoffrey.jpg


Warning
-------

Geoffrey is a work in progress project.

If you want to see a proof of concept checkout the tag `v0.0.1` and follow the README.

Running the tests
-----------------

We recommend to use Vagrant as testing environment.

.. code-block:: bash

   $ make vagrant-test

Another aproach is using a simple virtualenv (with python 3.3+), and
execute:

.. code-block:: bash

   $ make test-all


Status
------

.. image:: https://coveralls.io/repos/nilp0inter/geoffrey/badge.png?branch=develop
   :target: https://coveralls.io/r/nilp0inter/geoffrey?branch=develop

.. image:: https://travis-ci.org/nilp0inter/geoffrey.svg?branch=develop
   :target: https://travis-ci.org/nilp0inter/geoffrey

.. image:: https://badge.waffle.io/nilp0inter/geoffrey.png?label=wip&title=WIP
   :target: https://waffle.io/nilp0inter/geoffrey 
   :alt: 'Stories in WIP'
