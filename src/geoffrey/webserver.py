import os
import json
import uuid

from bottle import run
from bottle import request
from bottle import response
from bottle import HTTPError
from bottle import static_file, TEMPLATE_PATH, jinja2_view

from geoffrey.deps.aiobottle import AsyncBottle
from geoffrey.deps.aiobottle import AsyncServer

from geoffrey import utils
from geoffrey.subscription import Consumer
from geoffrey.plugin import get_all_plugins


class WebServer:
    """
    The Webserver of Geoffrey.

    Support the API and web resources.
    At this time this does not handle the websocket; is handled by the
    Websocket class.

    """
    def __init__(self, server, bottle=AsyncBottle):
        self.server = server
        self.webbase = os.path.join(os.path.dirname(__file__), "web")
        TEMPLATE_PATH[:] = [self.webbase]
        self.config = server.config

        # Websocket address
        self.websocket_server_port = self.config.getint(
            'geoffrey', 'websocket_server_port', fallback=8701)

        # Webserver address
        self.host = self.config.get(
            'geoffrey', 'http_server_host', fallback='127.0.0.1')
        self.port = self.config.getint(
            'geoffrey', 'http_server_port', fallback=8700)

        #
        # Bottle `app` definition
        #
        self.app = bottle()

        self.app.route('/', method='GET', callback=self.index)
        self.app.route('/index.html', method='GET', callback=self.index)
        self.app.route('/assets/<filepath:path>',
                       method='GET', callback=self.server_static)
        self.app.route('/plugins/<filepath:path>',
                       method='GET', callback=self.server_plugin_static)

        # API self description
        self.app.route('/api/v1', method='GET', callback=self.get_api)

        # Consumer API
        self.app.route('/api/v1/consumer',
                       method='POST', callback=self.consumer)
        self.app.route('/api/v1/consumer/<consumer_id>',
                       method='DELETE', callback=self.consumer)

        # Project API
        self.app.route('/api/v1/projects',
                       method='GET', callback=self.get_projects)

        # Plugins API
        self.app.route('/api/v1/<project_id>/plugins',
                       method='GET', callback=self.get_plugins)
        self.app.route('/api/v1/<project_id>/<plugin_id>/source/<language>',
                       method='GET', callback=self.plugin_source)
        self.app.route('/api/v1/<project_id>/<plugin_id>/state',
                       method='GET', callback=self.plugin_state)

        # Subscription API
        self.app.route('/api/v1/subscription/<consumer_id>',
                       method='POST', callback=self.subscribe)

    def consumer(self, consumer_id=None):
        """ Register a consumer. """
        if request.method == 'POST':
            consumer_uuid = str(uuid.uuid4())

            new_consumer = Consumer()
            self.server.consumers[consumer_uuid] = new_consumer
            self.server.hub.subscriptions.append(new_consumer)
            websocket_port = self.server.config.getint('geoffrey',
                                                       'websocket_server_port',
                                                       fallback=8701)
            websocket_address = request.get_header('host').split(':', 1)[0]
            ws = 'ws://{address}:{port}'.format(address=websocket_address,
                                                port=websocket_port)
            response.content_type = 'application/json'
            return json.dumps({'id': consumer_uuid,
                               'ws': ws})
        else:
            try:
                self.server.consumers.pop(consumer_id)
            except KeyError:
                raise HTTPError(404, 'Consumer not registered.')

    def get_projects(self):
        """ Return the current projects. """
        projects = []
        for project in self.server.projects:
            projects.append({'id': utils.slugify(project),
                             'name': project})
        response.content_type = 'application/json'
        return json.dumps(projects)

    # PLUGIN API
    def get_plugins(self, project_id):
        """ Return the active plugins of `project_id`. """
        response.content_type = 'application/json'
        project_plugins = self.server.projects[project_id].plugins
        plugins = []
        for plugin in project_plugins.keys():
            plugins.append({'id': plugin})
        return json.dumps(plugins)

    def plugin_source(self, project_id, plugin_id, language):
        """
        Return the `main` plugin source of this plugin for the given
        language.

        """
        try:
            project = self.server.projects[project_id]
            plugin = project.plugins[plugin_id]
            fullpath = plugin.client_plugin_source(language)
        except (KeyError, ValueError):
            raise HTTPError(404)
        else:
            if fullpath is None:
                raise HTTPError(404)
            else:
                root = os.path.dirname(fullpath)
                filename = os.path.basename(fullpath)
                return static_file(filename, root=root)

    def plugin_state(self, project_id, plugin_id):
        """ Return the list of states of this plugin. """
        from geoffrey.data import DataKey
        criteria = DataKey(project=project_id, plugin=plugin_id, key=None)
        response.content_type = 'application/json'
        return json.dumps([s.serializable()
                           for s in self.server.hub.get_states(criteria)])

    def subscribe(self, consumer_id):
        """ Change the subscription criteria of this consumer. """
        try:
            consumer = self.server.consumers[consumer_id]
        except KeyError:
            raise HTTPError(404, 'Consumer not registered.')
        else:
            try:
                if not "criteria" in request.json:
                    raise ValueError("'criteria' key is mandatory.")

                criteria = request.json["criteria"]

                if not isinstance(criteria, list):
                    raise ValueError("criteria must be a list")

                for c in criteria:
                    if not isinstance(c, dict):
                        raise ValueError("criteria elements must be dictionaries")
                    for key, value in c.items():
                        if not isinstance(key, str) or \
                                not isinstance(value, str):
                            raise ValueError("invalid data type")
            except Exception as err:
                raise HTTPError(400, err)
            else:
                consumer.criteria = criteria

    @jinja2_view('index.html')
    def index(self):
        """ Serve index.html redered with jinja2. """
        return {}

    def server_static(self, filepath):
        """ Serve static files under web/assets at /assets. """
        root = os.path.join(self.webbase, 'assets')
        return static_file(filepath, root=root)

    def server_plugin_static(self, filepath):
        """ Serve static files under pluginname/assets. """
        try:
            pluginname, filename = filepath.split('/', 1)
        except:
            raise HTTPError(404, "invalid plugin name")

        plugins = get_all_plugins(self.config, project=None)
        for plugin in plugins:
            if plugin.name == pluginname:
                root = plugin.assets
                if root is not None:
                    return static_file(filename, root=root)
                else:
                    raise HTTPError(404, "no assets for this plugin")
        plugins = get_all_plugins(self.config, project=None)

        raise HTTPError(404, "plugin not found" + pluginname + str([plugin.name for plugin in plugins]))


    # Get web API definitions
    def get_api(self):
        """ Return a list of endpoints for documentation. """
        from cgi import escape
        routes = {escape(route.rule)
                  for route in self.app.routes
                  if route.rule.startswith('/api')}
        html_list = '<ul>'
        for route in sorted(routes):
            html_list += '<li>{}</li>'.format(route)
        html_list += '</ul>'
        return html_list

    def start(self):
        """ Run the internal webserver. """
        run(self.app, host=self.host, port=self.port, server=AsyncServer,
            quiet=True, debug=False)
