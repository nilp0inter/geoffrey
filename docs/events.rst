Event data type
===============


.. code-block:: javascript

   {
     'source': 'server_plugin_id',
     'key': '<defined by plugin>',
     'value': ...,  # Content and type defined by plugin.
   }


Filesystem event example:

.. code-block:: javascript

   {
     'source': 'FileSystem',
     'key': '/home/nil/mifichero.py',
     'value': {'type': 'modification', 'timestamp': ..., 'md5': 'ddd'}
   }
