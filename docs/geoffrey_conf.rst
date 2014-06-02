geoffrey.conf
=============

Main configuration file of geoffrey server.

``[geoffrey]`` Section Settings
-------------------------------

This section contains the global configuration of the server.

``[geoffrey]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``http_server_host``

  Web server bind address.

  *Default*: ``127.0.0.1``

  *Required*: No.

  *Introduced*: 0.1.0

``http_server_port``

  Web server TCP port.

  *Default*: ``8700``

  *Required*: No.

  *Introduced*: 0.1.0


``websocket_server_host``

  Websocket bind address.

  *Default*: ``127.0.0.1``

  *Required*: No.

  *Introduced*: 0.1.0

``websocket_server_port``

  Websocket TCP port.

  *Default*: ``8701``

  *Required*: No.

  *Introduced*: 0.1.0

``[projects]`` Section Settings
-------------------------------

Projects global configuration section.

``[projects]`` Section Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``root``

  Root of the projects directory.

  *Default*: ``~/.geoffrey/projects``

  *Required*: No.

  *Introduced*: 0.1.0

