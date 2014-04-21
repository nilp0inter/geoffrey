
from geoffrey.deps.straight.plugin import load
from geoffrey.deps.straight.plugin.manager import PluginManager


class GeoffreyPlugin:
    """
    Base plugin.

    """

    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def _section_name(self):
        return 'plugin:' + self.name

    def is_enabled(self):
        section_name = self._section_name
        return section_name in self.config.sections()


def get_plugins(config, *args, **kwargs):
    loader = load('geoffrey.plugins',
                  subclasses=GeoffreyPlugin)

    all_plugins = loader.produce(
        config, *args, **kwargs)

    return PluginManager([plugin for plugin in all_plugins if plugin.is_enabled()])
