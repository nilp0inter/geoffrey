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
expresión AND. El conjunto de subscripciones se evaluarán como una expresión
OR.  Cada evento se enviará solamente una vez independientemente del número de
subscripciones con las que concuerde.


Eventos
-------

Cada elemento que se transmite desde el Server al UI es un evento serializado
en formato JSON.

Los eventos tienen los siguientes atributos básicos:

  * timestamp: Marca de tiempo de generación del evento.
  * hostname: Host donde se originó el evento.
  * username: Nombre del usuario que ha generado el evento.
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
  * metric: Estadísticas/métricas.
  * version: Especio de nombres reservado al sistema de control de versiones.


Tipos de eventos
----------------

Tipos de eventos de un objeto.

  * created: Un objeto ha sido creado.
  * deleted: Un objeto ha sido borrado.
  * changed: Un objeto ha cambiado.
  * discovered. Un objeto ha sido descubierto.
  * status. Un objeto ha sido (re)descubierto por petición del UI.


Ejemplos
--------


Informa de una diferencia con respecto a la última versión de un fichero.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   {
     "timestamp":1395080527.091157,
     "hostname":"absolut",
     "username":"nil",
     "namespace":"filesystem",
     "object":"/home/nil/Projects/geoffrey/setup.py",
     "type":"changed",
     "source":"filediff",
     "data":{"patch": "..."}
   }


Se ha borrado un fichero del disco.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   {
     "timestamp":1395080527.091157,
     "hostname":"absolut",
     "username":"nil",
     "namespace":"filesystem",
     "object":"/home/nil/Projects/geoffrey/deleteme.txt",
     "type":"deleted",
     "source":"filesystem",
     "data":null
   }


Se ha descubierto un nuevo fichero en el disco (eventos que se generan al iniciar el servidor).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

  {
    "timestamp":1395081923.66807,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "object":"/home/nil/Projects/geoffrey",
    "type":"discovered",
    "source":"filesystem",
    "data":{"type": "dir"}
  }


Salida del plugin pylint.
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

  {
    "timestamp":1395083786.396037,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "object":"/home/nil/Projects/geoffrey/example.py",
    "type":"changed",
    "source":"pylint",
    "data":[
      {"message": "Missing docstring", "line": "1"},
      {"message": "Unable to import 'iptools.ipv4'", "line": "10"},
      {"message": "Unable to import 'netinfo'", "line": "11"},
      {"message": "Unable to import 'netinfo'", "line": "12"},
      {"message": "Unable to import 'nmap'", "line": "13"},
      {"message": "Invalid name \"blacklist\" for type constant (should match (([A-Z_][A-Z0-9_]*)|(__.*__))$)", "line": "15"},
      {"message": "Invalid name \"whitelist\" for type constant (should match (([A-Z_][A-Z0-9_]*)|(__.*__))$)", "line": "19"},
      {"message": "Missing docstring", "line": "37"},
      {"message": "Missing docstring", "line": "43"},
      {"message": "Invalid name \"ps\" for type variable (should match [a-z_][a-z0-9_]{2,30}$)", "line": "44"},
      {"message": "Unused variable 'gateway'", "line": "46"},
      {"message": "Missing docstring", "line": "60"},
      {"message": "Missing docstring", "line": "65"},
      {"message": "Missing docstring", "line": "77"},
      {"message": "Missing docstring", "line": "91"},
      {"message": "Unused variable 'i'", "line": "97"}, {"message": "Missing docstring", "line": "103"}
    ]
  }

Eventos múltiples
-----------------

Es posible enviar múltiples eventos en un único mensaje con el objetivo de
reducir la cantidad de información.

  * Se añadirá una clave `events` que contendrá obligatoriamente una lista de
    diccionarios.
  * Cada uno de estos diccionarios se convertirá en un evento compuesto por
    las claves y valores que contiene el diccionario.
  * Si alguno de los diccionarios no contiene las claves obligatorias
    defecto, por las claves y valores del nivel principal.

Ejemplos
~~~~~~~~

Descubrimiento de una serie de ficheros (habitual al iniciar el server).

El siguiente *evento múltiple*:

.. code-block:: javascript

  {
    "timestamp":1395082711.730503,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "type":"discovered",
    "source":"filesystem",
    "events":[
       {"object": "/home/nil/Projects/geoffrey",
        "data": {"type": "dir"}},
       {"object": "/home/nil/Projects/geoffrey/setup.py",
        "data": {"type": "file"}},
       {"object": "/home/nil/Projects/geoffrey/README.txt",
        "data": {"type": "file"}}
    ]
  }


Es equivalente a estos 3 eventos sencillos:

.. code-block:: javascript

  {
    "timestamp":1395082711.730503,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "object":"/home/nil/Projects/geoffrey",
    "type":"discovered",
    "source":"filesystem",
    "data":{"type": "dir"}
  }
  {
    "timestamp":1395082711.730503,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "object":"/home/nil/Projects/geoffrey/setup.py",
    "type":"discovered",
    "source":"filesystem",
    "data":{"type": "file"}
  }
  {
    "timestamp":1395082711.730503,
    "hostname":"absolut",
    "username":"nil",
    "namespace":"filesystem",
    "object":"/home/nil/Projects/geoffrey/README.txt",
    "type":"discovered",
    "source":"filesystem",
    "data":{"type": "file"}
  }
