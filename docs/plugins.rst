The plugin architecture
=======================

Server side plugins
===================

A Geoffrey can define its own api endpoints for plugin specific task. To use this functionality one must define the method ``configure_app`` in the plugin class and add routes to the plugin's instance of app.

Example:
.. code-block:: python

   class Plugin(GeoffreyPlugin):
       def configure_app(self):
           self.app.rounte('/<method>', callback=self.pluginmethod)

       def pluginmethod(self):
           # super cool method magic specific for plugin

This path is relative to /api/v1/<project_id>/<plugin_id>/method/

.. note:: 

   Plugin routes **MUST** be precedeed by a /

Client side plugins
===================

Standard plugin list
====================

Third party plugins
===================
