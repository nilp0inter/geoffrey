import configparser


class Project:
    """Geoffrey project."""
    def __init__(self, name, config):
        self.name = name
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.plugins = {s.split(':')[1]: None
                        for s in self.config.sections()
                        if s.startswith('plugin:')}
