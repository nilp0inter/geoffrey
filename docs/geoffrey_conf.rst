geoffrey.conf
=============

Fichero de configuración principal.

``[geoffrey]`` Section Settings
-------------------------------

Contiene la configuración global del servidor.

``[geoffrey]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``http_server_host``

  La dirección de red donde el servidor web de geoffrey escuchará.

  *Default*: ``127.0.0.1``

  *Required*: No.

  *Introduced*: 0.1.0

``http_server_port``

  El puerto TCP donde el servidor web de geoffrey escuchará.

  *Default*: ``8700``

  *Required*: No.

  *Introduced*: 0.1.0


``websocket_server_host``

  La dirección de red donde el servidor de websockets de geoffrey escuchará.

  *Default*: ``127.0.0.1``

  *Required*: No.

  *Introduced*: 0.1.0

``websocket_server_port``

  El puerto TCP donde el servidor de websockets de geoffrey escuchará.

  *Default*: ``8701``

  *Required*: No.

  *Introduced*: 0.1.0

``[projects]`` Section Settings
-------------------------------

Configuración global de proyectos.

``[projects]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``root``

  Raíz del directorio de proyectos de geoffrey.

  *Default*: ``~/.geoffrey/projects``

  *Required*: No.

  *Introduced*: 0.1.0

