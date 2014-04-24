import os
import logging
import configparser
from geoffrey import utils, defaults, plugin
from geoffrey.hub import EventHUB

logger = logging.getLogger(__name__)


class Project:
    """Geoffrey project."""
    def __init__(self, name, config):
        self.name = name
        self.hub = EventHUB()
        self.configfile = config
        if not os.path.exists(config):
            utils.write_template(config, defaults.PROJECT_CONFIG_DEFAULT)
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.plugins = {p.name: p
                        for p in plugin.get_plugins(self.config, self.hub)}
        # Add subscriptions of all plugins to the hub
        for p in self.plugins.values():
            subscriptions = p.subscriptions
            if subscriptions:
                self.hub.add_subscriptions(subscriptions)

        logger.debug("Project: %r, Active plugins: %r", self.name, self.plugins)

    def remove(self):
        """Remove this project from disk."""

        os.unlink(self.configfile)
        os.removedirs(os.path.dirname(self.configfile))
