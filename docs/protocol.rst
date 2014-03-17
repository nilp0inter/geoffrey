.. todo:: Traducir

Protocolo
=========

El protocolo de Geoffrey se basa en la transferencia de documentos JSON a
través de un websocket.

Definiremos los siguientes actores:

                    FS -> Geoffrey Server -> Geoffrey UI

  * FS: El sistema de ficheros que está siendo monitorizado por Geoffrey
    Server.

  * Geoffrey Server: Proceso encargado de disparar los plugins adecuados ante
    los eventos del FS, procesar su salida, y enviar la información a `Geoffrey UI`
    via `Geoffrey Protocol`.

  * Geoffrey UI: Frontal que mostrará los datos al usuario. Geoffrey
    proporciona un frontal web por defecto; pero sería posible escribir frontales
    para editores de texto, terminales de texto, etc.

El protocolo que describiremos a continuación es el que se utilizará para la
transmisión de información entre `Geoffrey Server` y `Geoffrey UI`.

Alta de UI
----------

El UI debe registrarse en el server para poder recibir información.
Hacer una petición POST a XXX, el server devolverá el identificador único de UI.

Subscripción
------------

El UI debe informar al server que quiere recibir cierto tipo de eventos.
Para ello debe hacer una petición POST a XXX con los siguientes parámetros:

  * ui_id: Identificador único de UI devuelto en el proceso de alta.
  * from: Marca de tiempo desde la que recibir los eventos. Si no se especifica
    se recibirán todos.
  * <key>: <fnmatch>

El conjunto de claves dispuestas en cada subscripción se evaluarán como una
expresión AND. El conjunto de subscripciones se evaluarán como una expresión OR.
Cada evento se enviará solamente una vez independientemente del número de
subscripciones con las que concuerde.

Eventos
-------

Cada elemento que se transmite desde el Server al UI es un evento serializado
en formato JSON.

Los eventos tienen los siguientes atributos básicos:

  * timestamp: Marca de tiempo de generación del evento.
  * namespace: Espacio de nombres donde se encuentra el objeto
  * object: Nombre del objeto al que hace referencia el evento.
  * type: Tipo de evento transmitido.
  * source: Generador del evento (detector).
  * data: Datos del evento (Específico de cada source).

Namespaces
----------

Un namespace es un conjunto de objetos con nombres únicos para cada namespace.

  * filesystem: Sistemas de ficheros que se está monitorizando.
  * server: Servidor de Geoffrey.
  * plugin: Sistema de plugins.
  * project: Espacio de nombres para proyectos.
  * statistics: Estadísticas.
  * version: Especio de nombres reservado al sistema de control de versiones.

Tipos de eventos
----------------

Tipos de eventos de un objeto.

  * create
  * delete
  * change
