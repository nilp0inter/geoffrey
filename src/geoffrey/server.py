import os
import asyncio
import signal
import configparser

from .project import Project

DEFAULT_CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.geoffrey')
DEFAULT_CONFIG_FILENAME = os.path.join(DEFAULT_CONFIG_ROOT, 'geoffrey.conf')


class Server:
    """The Geoffrey server."""
    def __init__(self, config=DEFAULT_CONFIG_FILENAME):
        self.config = self.read_main_config(filename=config)
        self.projects = {}
        default_projects_root = os.path.join(
            os.path.dirname(config), 'projects')
        projects_root = self.config.get('projects', 'root',
                                        fallback=default_projects_root)
        if not os.path.isdir(projects_root):
            os.makedirs(projects_root)

        self.projects = {}
        for name in os.listdir(projects_root):
            project_root = os.path.join(projects_root, name)
            if os.path.isdir(project_root):
                project_config = os.path.join(project_root,
                                              '{}.conf'.format(name))
                if os.path.isfile(project_config):
                    self.projects[name] = Project(name=name,
                                                  config=project_config)

        self.loop = asyncio.get_event_loop()

    @staticmethod
    def read_main_config(filename=DEFAULT_CONFIG_FILENAME):
        """Read server configuration."""
        config = configparser.ConfigParser()

        if os.path.exists(filename):
            if os.path.isfile(filename):
                config.read(filename)
            else:
                raise TypeError('Config file is not a regular file.')
        else:
            # Config does not exists. Create the default one.

            root = os.path.dirname(filename)
            if not os.path.exists(root):
                os.makedirs(root)

            with open(filename, 'w+') as file_:
                file_.write('[geoffrey]\n\n')
                file_.seek(0)
                config.read_file(file_)

        return config

    def handle_ctrl_c(self):
        """Control Ctrl-C to the server."""
        # TODO: Use logging
        print("Exiting...")
        self.loop.stop()

    def run(self):
        """Run the server."""

        self.loop.add_signal_handler(signal.SIGINT, self.handle_ctrl_c)

        self.start_webserver()
        self.loop.run_forever()

    def start_webserver(self):
        """Run the internal webserver."""
        from geoffrey.deps.aiobottle import AsyncBottle, AsyncServer
        from bottle import run

        app = AsyncBottle()

        @app.get('/')
        def index():
            return "Geoffrey"

        run(app, host='localhost', port=8700, server=AsyncServer)
