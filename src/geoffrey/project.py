import os
import configparser
from geoffrey import utils, defaults, plugin


class Project:
    """Geoffrey project."""
    def __init__(self, name, config):
        self.name = name
        self.configfile = config
        if not os.path.exists(config):
            utils.write_template(config, defaults.PROJECT_CONFIG_DEFAULT)
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.plugins = {p.name: p for p in plugin.get_plugins(self.config)}

    def remove(self):
        """Remove this project from disk."""

        os.unlink(self.configfile)
        os.removedirs(os.path.dirname(self.configfile))
