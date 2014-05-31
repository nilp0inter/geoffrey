API v1
======

Consumer API
------------

Register
~~~~~~~~

POST /api/v1/consumer

.. code-block:: javascript

   {
     'id': 'ab37-3f47...',
     'ws': 'ws://127.0.0.1:8701',
   }


Unregister
~~~~~~~~~~

DELETE /api/v1/consumer/<consumer_id>


Project API
-----------

Retrieve the project list
~~~~~~~~~~~~~~~~~~~~~~~~~

GET /api/v1/projects

.. code-block:: javascript

   [
     {'id': 'project_a',
      'name': 'Project A'},
     {'id': 'project_b',
      'name': 'Project B'}
   ]


Plugin API
----------

Retrieve plugin list
~~~~~~~~~~~~~~~~~~~~

GET /api/v1/<project_id>/plugins

.. code-block:: javascript

   [
     {'id': 'pylint'}
   ]


Example::

   GET /api/v1/project_a/plugins


Retrieve plugin source
~~~~~~~~~~~~~~~~~~~~~~

GET /api/v1/<project_id>/<plugin_id>/source/<language>

.. code-block:: javascript

   [javascript plugin source]


Retrieve plugin state
~~~~~~~~~~~~~~~~~~~~~

GET /api/v1/<project_id>/<plugin_id>/state

.. code-block:: javascript

   [
     {...},
     {...},
   ]


Subscription API
----------------

Make subscriptions
~~~~~~~~~~~~~~~~~~

POST /api/v1/subscription/<consumer_id>

.. code-block:: javascript

   [
     {<plugin_1_subscription_data>},
     {<plugin_2_subscription_data>},
     {<plugin_3_subscription_data>},
   ]

Consecutive requests will override the subscription list for this
consumer.
