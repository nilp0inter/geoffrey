from geoffrey.datamanager import DataManager
from geoffrey.pluginmanager import PluginManager


class Project:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.dm = DataManager()
        self.pm = PluginManager()
