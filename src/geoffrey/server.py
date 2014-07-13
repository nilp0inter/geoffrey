import asyncio
import configparser
import logging
import os
import signal

import websockets

from .project import Project
from geoffrey import defaults
from geoffrey import hub
from geoffrey import utils
from geoffrey.websocket import WebsocketServer

from geoffrey.webserver import WebServer


DEFAULT_CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.geoffrey')
DEFAULT_CONFIG_FILENAME = os.path.join(DEFAULT_CONFIG_ROOT, 'geoffrey.conf')
STATES_FILE = os.path.join(DEFAULT_CONFIG_ROOT, 'states.pickle')

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
        self.projects = self._get_projects()
        self.hub = hub.get_hub()
        # Strong references of the server's tasks to prevent garbage
        # collection.
        self.tasks = []
        self.consumers = {}

        if os.path.isfile(STATES_FILE):
            self.hub.restore_states(STATES_FILE)

    @property
    def projects_root(self):
        """Returns the projects directory."""
        return self.config.get(
            'projects', 'root',
            fallback=os.path.join(os.path.dirname(self.configfile),
                                  'projects'))

    def _get_projects(self):
        """Gets all the projects."""
        projects = {}
        for name in os.listdir(self.projects_root):
            project_root = os.path.join(self.projects_root, name)
            if os.path.isdir(project_root):
                project_config = os.path.join(project_root, 'project.conf')
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
        self.hub.save_states(STATES_FILE)
        self.loop.stop()

    def run(self):
        """Run the server."""

        websocket_server_host = self.config.get(
            'geoffrey', 'websocket_server_host', fallback='127.0.0.1')
        websocket_server_port = self.config.getint(
            'geoffrey', 'websocket_server_port', fallback=8701)

        self.loop.add_signal_handler(signal.SIGINT, self.handle_ctrl_c)

        # WEBSERVER
        web_app = WebServer(server=self)
        web_app.start()

        # WEBSOCKET SERVER
        wss = websockets.serve(WebsocketServer(self.consumers).server,
                               websocket_server_host,
                               websocket_server_port)
        self.tasks.append(asyncio.Task(wss))

        # HUB
        self.tasks.append(asyncio.Task(self.hub.run()))

        logger.debug("Starting the main loop.")
        self.loop.run_forever()

    def create_project(self, project_name):
        """Create a new project."""
        project_root = os.path.join(self.projects_root, project_name)
        os.makedirs(project_root)
        project_config = os.path.join(project_root, 'project.conf')
        self.projects[project_name] = Project(name=project_name,
                                              config=project_config)

    def delete_project(self, project_name):
        """Delete a project."""
        if project_name in self.projects:
            project = self.projects.pop(project_name)
            project.remove()
        else:
            raise RuntimeError("Geoffrey can't delete unmanaged projects.")
