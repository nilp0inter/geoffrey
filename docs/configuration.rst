Configuration
=============

Server configuration
--------------------

Configuration structure
~~~~~~~~~~~~~~~~~~~~~~~

Geoffrey maintains all its configuration in ini-style files.

There is a global server configuration and a per project configuration.

The default location of the server configuration is::

  ~/.geoffrey/geoffrey.conf

The symbol `~` is replaced with the location of the HOME directory of the user running Geoffrey.

The configuration files are divided in sections with this sintax::

  [section name]

Each section contains key-value pairs::

  key = value

This is an example configuration structure.

.. code-block:: bash

    ~/.geoffrey/
    ├── geoffrey.conf
    └── projects/
        ├── project_1
        │   ├── data/
        │   │   └── [...]
        │   └── project_1.conf
        └── project_2/
            ├── data/
            │   └── [...]
            └── project_2.conf
