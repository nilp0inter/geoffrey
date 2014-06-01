import asyncio
import configparser
import logging
import os
import json
import signal
import uuid

import websockets

from .project import Project
from geoffrey import defaults
from geoffrey import hub
from geoffrey import utils
from geoffrey.websocket import WebsocketServer
from geoffrey.subscription import Consumer

from geoffrey.deps.aiobottle import AsyncBottle

DEFAULT_CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.geoffrey')
DEFAULT_CONFIG_FILENAME = os.path.join(DEFAULT_CONFIG_ROOT, 'geoffrey.conf')

logger = logging.getLogger(__name__)


class Server:

    """The Geoffrey server."""

    def __init__(self, config=DEFAULT_CONFIG_FILENAME):
        logger.info("Starting Geoffrey server!")
        self.configfile = config
        self.config = self.read_main_config(filename=self.configfile)

        if not os.path.isdir(self.projects_root):
            os.makedirs(self.projects_root)

        self.loop = asyncio.get_event_loop()
        self.projects = self.get_projects()
        self.hub = hub.get_hub()
        # Strong references of the server's tasks to prevent garbage
        # collection.
        self.tasks = []
        self.consumers = {}

    @property
    def projects_root(self):
        """Returns the projects directory."""
        return self.config.get(
            'projects', 'root',
            fallback=os.path.join(os.path.dirname(self.configfile),
                                  'projects'))

    def get_projects(self):
        """Gets all the projects."""
        projects = {}
        for name in os.listdir(self.projects_root):
            project_root = os.path.join(self.projects_root, name)
            if os.path.isdir(project_root):
                project_config = os.path.join(project_root,
                                              '{}.conf'.format(name))
                if os.path.isfile(project_config):
                    projects[name] = Project(name=name, config=project_config)

        return projects

    @staticmethod
    def read_main_config(filename=DEFAULT_CONFIG_FILENAME):
        """Read server configuration."""
        config = configparser.ConfigParser()

        if os.path.exists(filename):
            if not os.path.isfile(filename):
                raise TypeError('Config file is not a regular file.')
        else:
            # Config does not exists. Create the default one.

            root = os.path.dirname(filename)
            if not os.path.exists(root):
                os.makedirs(root)

            utils.write_template(filename, defaults.GEOFFREY_CONFIG_DEFAULT)

        config.read(filename)
        return config

    def handle_ctrl_c(self):
        """Control Ctrl-C to the server."""
        logger.warning("Pressed Ctrl-C. Exiting.")
        self.loop.stop()

    def run(self):
        """Run the server."""

        websocket_server_host = self.config.get(
            'geoffrey', 'websocket_server_host', fallback='127.0.0.1')
        websocket_server_port = self.config.getint(
            'geoffrey', 'websocket_server_port', fallback=8701)

        self.loop.add_signal_handler(signal.SIGINT, self.handle_ctrl_c)

        # WEBSERVER
        self.start_webserver()

        # WEBSOCKET SERVER
        wss = websockets.serve(WebsocketServer(self.consumers).server,
                               websocket_server_host,
                               websocket_server_port)
        self.tasks.append(asyncio.Task(wss))

        # HUB
        self.tasks.append(asyncio.Task(self.hub.run()))

        logger.debug("Starting the main loop.")
        self.loop.run_forever()

    def get_webapp(self, bottle=AsyncBottle):
        """Return the bottle application of the server."""
        from bottle import static_file, TEMPLATE_PATH, jinja2_view, request
        from bottle import response
        from bottle import HTTPError

        webbase = os.path.join(os.path.dirname(__file__), "web")
        TEMPLATE_PATH[:] = [webbase]

        websocket_server_host = self.config.get('geoffrey',
                                                'websocket_server_host',
                                                fallback='127.0.0.1')

        websocket_server_port = self.config.getint('geoffrey',
                                                   'websocket_server_port',
                                                   fallback=8701)

        app = bottle()

        # CONSUMER API
        @app.post('/api/v1/consumer')
        @app.delete('/api/v1/consumer/<consumer_id>')
        def consumer(consumer_id=None):
            """ Register a consumer """

            if request.method == 'POST':
                consumer_uuid = str(uuid.uuid4())

                new_consumer = Consumer()
                self.consumers[consumer_uuid] = new_consumer
                self.hub.subscriptions.append(new_consumer)

                response.content_type = 'application/json'
                return json.dumps({'id': consumer_uuid,
                                   'ws': 'ws://127.0.0.1:8701'})
            else:
                try:
                    removed_consumer = self.consumers.pop(consumer_id)
                except KeyError:
                    raise HTTPError(404, 'Consumer not registered.')

        # PROJECT API
        @app.get('/api/v1/projects')
        def get_projects():

            projects = []
            for project in self.get_projects():
                projects.append({'id': utils.slugify(project),
                                 'name': project})
            response.content_type = 'application/json'
            return json.dumps(projects)

        # PLUGIN API
        @app.get('/api/v1/<project_id>/plugins')
        def get_plugins(project_id):
            response.content_type = 'application/json'
            return json.dumps([{'id': 'pylint'}])

        @app.get('/api/v1/<project_id>/<plugin_id>/source/<language>')
        def plugin_source(project_id, plugin_id, language):

            return '<script type="text/javascript">'

        @app.get('/api/v1/<project_id>/<plugin_id>/state')
        def plugin_state(project_id, plugin_id):
            from geoffrey.state import StateKey
            criteria = StateKey(project=project_id, plugin=plugin_id, key=None)
            response.content_type = 'application/json'
            return json.dumps([s.serializable()
                               for s in self.hub.get_states(criteria)])

        @app.post('/api/v1/subscription/<consumer_id>')
        def subscribe(consumer_id):
            try:
                consumer = self.consumers[consumer_id]
                criteria = json.loads(request.POST['criteria'])
            except KeyError:
                raise HTTPError(404, 'Consumer not registered.')
            except:
                raise HTTPError(400, 'Bad request.')
            else:
                consumer.criteria = criteria

        @app.get('/')
        @jinja2_view('index.html')
        def index():
            """Serve index.html redered with jinja2."""
            return {'host': websocket_server_host,
                    'port': websocket_server_port}

        @app.get('/assets/<filepath:path>')
        def server_static(filepath):
            """Serve static files under web/assets at /assets."""
            return static_file(filepath, root=os.path.join(webbase, 'assets'))

        # Get web API definitions
        @app.get('/api/v1')
        def get_api():
            from cgi import escape
            routes = {escape(route.rule)
                      for route in app.routes
                      if route.rule.startswith('/api') }
            html_list = '<ul>'
            for route in routes:
                html_list += '<li>{}</li>'.format(route)
            html_list += '</ul>'
            return html_list

        return app

    def start_webserver(self):
        """Run the internal webserver."""
        from geoffrey.deps.aiobottle import AsyncServer
        from bottle import run
        http_server_host = self.config.get('geoffrey', 'http_server_host',
                                           fallback='127.0.0.1')

        http_server_port = self.config.getint('geoffrey', 'http_server_port',
                                              fallback=8700)

        app = self.get_webapp()
        run(app, host=http_server_host, port=http_server_port,
            server=AsyncServer, quiet=True, debug=False)

    def create_project(self, project_name):
        """Create a new project."""
        project_root = os.path.join(self.projects_root, project_name)
        os.makedirs(project_root)
        project_config = os.path.join(project_root,
                                      '{}.conf'.format(project_name))
        self.projects[project_name] = Project(name=project_name,
                                              config=project_config)

    def delete_project(self, project_name):
        """Delete a project."""
        if project_name in self.projects:
            project = self.projects.pop(project_name)
            project.remove()
        else:
            raise RuntimeError("Geoffrey can't delete unmanaged projects.")
