import configparser
import logging
import os

from geoffrey import utils, defaults
from geoffrey.plugin import get_plugins

logger = logging.getLogger(__name__)

class Project:
    """Geoffrey project."""
    def __init__(self, name, config):
        logger.info("Project found `%s`.", name)
        self.name = name

        # Load the project configuration.
        self.configfile = config
        if not os.path.exists(config):
            utils.write_template(config, defaults.PROJECT_CONFIG_DEFAULT)
        self.config = configparser.ConfigParser()
        self.config.read(config)

        # Create the list of plugins of this project.
        plugins = get_plugins(self.config, project=self)
        self.plugins = {plugin.name: plugin for plugin in plugins}

        logger.info("Project: `%s`. Plugins found: %s",
                    self.name, repr(list(self.plugins.values())))

        # Start the plugins of this project.
        for p in self.plugins.values():
            p.start()

        try:
            self.title = self.config.get('project', 'title')
        except:
            self.title = self.name

    def remove(self):
        """Remove this project from disk."""

        os.unlink(self.configfile)
        os.removedirs(os.path.dirname(self.configfile))

    @property
    def url(self):
        """Returns the web-ui url for this project."""
        return '/project/' + self.name
