import asyncio
import configparser
import os
import signal


DEFAULT_CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.geoffrey')
DEFAULT_CONFIG_FILENAME = os.path.join(DEFAULT_CONFIG_ROOT, 'geoffrey.conf')


class Server:
    """
    The geoffrey server.

    """
    def __init__(self, config=DEFAULT_CONFIG_FILENAME):
        self.config = self.read_main_config(filename=config)
        self.projects = {}
        default_projects_root = os.path.join(
            os.path.dirname(config), 'projects')
        project_root = self.config.get('projects', 'root',
                                       fallback=default_projects_root)
        if not os.path.isdir(project_root):
            os.makedirs(project_root)
        self.projects = {name: os.path.join(project_root, name)
                         for name in os.listdir(project_root)
                         if os.path.isdir(os.path.join(project_root, name))}
        self.loop = asyncio.get_event_loop()

    @staticmethod
    def read_main_config(filename=DEFAULT_CONFIG_FILENAME):
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

            with open(filename, 'w+') as f:
                f.write('[geoffrey]\n\n')
                f.seek(0)
                config.read_file(f)

        return config

    def handle_ctrl_c(self):
        # TODO: Use logging
        print("Exiting...")
        self.loop.stop()

    def run(self):
        self.loop.add_signal_handler(signal.SIGINT, self.handle_ctrl_c)
        self.loop.run_forever()


def main():
    server = Server()
    server.run()
