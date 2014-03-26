Configuration
=============

Server configuration
--------------------

Configuration structure
~~~~~~~~~~~~~~~~~~~~~~~

Geoffrey mantiene toda su configuración en ficheros de tipo .ini.
Existe una configuración global del servidor y además una configuración
específica por proyecto.

La localización por defecto del fichero de configuración del servidor es:

~/.geoffrey/geoffrey.conf

Donde ~ significa el directorio HOME del usuario.

Los ficheros de configuración se dividen en secciones del tipo:

[section name]

Que contienen pares clave valor del tipo:

key = value

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
