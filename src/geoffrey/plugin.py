
from geoffrey.deps.straight.plugin import load
from geoffrey.deps.straight.plugin.manager import PluginManager


class GeoffreyPlugin:
    """
    Base plugin.

    """

    def __init__(self, config):
        self.config = config

    def is_enabled(self):
        return True


def get_plugins(config, *args, **kwargs):
    all_plugins = load('geoffrey.plugins',
                       subclasses=GeoffreyPlugin).produce(config, *args, **kwargs)
    return PluginManager([plugin for plugin in all_plugins if plugin.is_enabled()])
