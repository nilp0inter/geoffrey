project_name.conf
=================

Fichero de configuración específico del proyecto (cada proyecto tendrá
uno propio).

``[project]`` Section Settings
------------------------------

Configuración global del proyecto.

``[project]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``data``

  Directorio donde se almacenarán los datos internos del proyecto.

  *Default*: ``~/.geoffrey/projects/project_name/data``

  *Required*: No.

  *Introduced*: 0.1.0


``[plugin:x]`` Section Settings
-------------------------------

El fichero de configuración del proyecto debe contener una o más
secciones ``plugin`` para que el servidor de geoffrey pueda obtener
datos del proyecto.

``[plugin:x]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


