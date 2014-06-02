API v1
======

Consumer API
------------

Register a new consumer
~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/v1/consumer

   :statuscode 200: no error

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/consumer HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json
   
      {
        "id": "84928d40-ea5a-11e3-9b27-0002a5d5c51b",
        "ws": "ws://127.0.0.1:8701"
      }


Unregister a consumer
~~~~~~~~~~~~~~~~~~~~~

.. http:delete:: /api/v1/consumer/(str:consumer_id)

   :param consumer_id: the unique identifier of the consumer given in the registration step
   :statuscode 200: no error
   :statuscode 404: consumer not found

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/consumer/84928d40-ea5a-11e3-9b27-0002a5d5c51b HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json
   

Project API
-----------

Retrieve the project list
~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/projects

   :statuscode 200: no error

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/projects HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": "project_a",
          "name": "Project A"
        },
        {
          "id": "project_b",
          "name": "Project B"
        }
      ]


Plugin API
----------

Retrieve the plugin list of specific project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/(str:project_id)/plugins

   :param project_id: the project identifier
   :statuscode 200: no error
   :statuscode 404: project does not exist

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/project_a/plugins HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": "pylint"
        },
        {
          "id": "filesystem"
        }
      ]


Retrieve the plugin source for the given language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/(str:project_id)/(str:plugin_id)/source/(str:language)

   :param project_id: the project identifier   
   :param plugin_id: the plugin identifier
   :param language: the extension of the file with the sources for this language
   :statuscode 200: no error

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/project_a/pylint/source/js HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json
   
      [javascript plugin source]


Retrieve the plugin states for the given project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GET /api/v1/<project_id>/<plugin_id>/state

.. http:get:: /api/v1/(str:project_id)/(str:plugin_id)/state

   :param project_id: the project identifier   
   :param plugin_id: the plugin identifier
   :statuscode 200: no error

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/project_a/pylint/state HTTP/1.1
      Host: localhost
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode :: http

      HTTP/1.1 200 OK
      Content-Type: application/json
   
      [
        {
          "project": "test",
          "key": "geoffrey/testspace/test.py",
          "plugin": "pylint",
          "value": {
            "exitcode": 16,
            "stdout": "No config ..."
          }
        }
      ]


Subscription API
----------------

Modify the consumer subscription list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

POST /api/v1/subscription/<consumer_id>

.. code-block:: javascript

   [
     {<plugin_1_subscription_data>},
     {<plugin_2_subscription_data>},
     {<plugin_3_subscription_data>},
   ]

Consecutive requests will override the subscription list for this
consumer.
