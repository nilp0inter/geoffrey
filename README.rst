Geoffrey
========

Geoffrey is a local continuous integration server.

.. image:: https://raw.githubusercontent.com/nilp0inter/geoffrey/develop/src/geoffrey/web/assets/geoffrey.jpg


* Documentation (spanish): http://geoffrey.readthedocs.org/en/latest/index.html


Dependencies
------------

Geoffrey works on Python>=3.3 .


Install
-------

Clone the repository and submodules:

.. code-block:: bash

   $ git clone --recursive https://github.com/nilp0inter/geoffrey.git
   $ cd geoffrey

Install as a standard python package:

.. code-block:: bash

   $ python setup.py install


Configuration file
------------------

By default `geoffrey` looks for its configuration file at ~/.geoffreyrc.

This is a configuration example:

.. code-block:: ini

   [geoffrey]
   host=127.0.0.1
   webserver_port=8700
   websocket_port=8701

   [plugin:pylint]
   IN_MODIFY=*.py

   [plugin:flake8]
   IN_MODIFY=*.py

   [plugin:radonraw]
   IN_MODIFY=*.py

   [plugin:radoncc]
   IN_MODIFY=*.py

   [plugin:radonmi]
   IN_MODIFY=*.py

   [plugin:pyreverse]
   IN_MODIFY=*.py

   [plugin:cheesecake]
   IN_CLOSE_WRITE=*/dist/*.tar.gz,*/dist/*.zip
   IN_MODIFY=*/dist/*.tar.gz,*/dist/*.zip

   [plugin:filediff]
   IN_MODIFY=*.py,*.txt,*.rst

Maybe you would like to install some tools before:

.. code-block:: bash

   $ sudo pip install pylint radon flake8 cheesecake
   $ sudo apt-get install graphviz

No virtualenv support for plugins at this moment, sorry.


Running
-------

1. Run `geoffrey` command and point to your working directory to start:

   .. code-block:: bash

      $ geoffrey /path/to/your/project

2. Open a browser and point to http://localhost:8700.
3. Make some modifications to any .py file in your project.
4. Enjoy the mess. :)


Develop
-------

We develop Geoffrey using Vagrant.

1. Install Vagrant from http://www.vagrantup.com/
2. Execute:

   .. code-block:: bash

      $ vagrant up

3. Your develop environment is up and running. You can modify the files and
   the changes will be reflected automatically in your vagrant box.

4. Enter into your vagrant box with:

   .. code-block:: bash

      $ vagrant ssh

5. Execute geoffrey:

   .. code-block:: bash

      $ geoffrey /home/vagrant

6. You can enter de UI from your system. Point your browser to:

   http://localhost:8700

