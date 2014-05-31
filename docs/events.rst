Event data type
===============


.. code-block:: javascript

   {
     'project': '<project_id>',
     'plugin': '<plugin_id>',
     'key': <defined by plugin (content & type)>,
     'value': <defined by plugin (content & type)>
   }


Filesystem event example:

.. code-block:: javascript

   {
     'project': 'project example',
     'plugin': 'FileSystem',
     'key': '/home/nil/mifichero.py',
     'value': {'type': 'modification', 'timestamp': ..., 'md5': 'ddd'}
   }
