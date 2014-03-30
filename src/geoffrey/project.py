import os
import configparser


class Project:
    """Geoffrey project."""
    def __init__(self, name, config):
        self.name = name
        if not os.path.exists(config):
            with open(config, 'w') as f:
                f.write('[project]\n\n')
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.plugins = {s.split(':')[1]: None
                        for s in self.config.sections()
                        if s.startswith('plugin:')}
