import os
import configparser

from geoffrey import default

GEOFFREY_CONFIG_TEMPLATE = """[geoffrey]
host={default.HOST}
webserver_port={default.WEBSERVER_PORT}
websocket_port={default.WEBSOCKET_PORT}
""".format(default=default)


class Config(configparser.ConfigParser):

    # Singleton per filename.
    _CONFIGS = {}

    def __new__(cls, filename, *args, **kwargs):
        if filename in cls._CONFIGS:
            return cls._CONFIGS[filename]
        else:
            instance = super().__new__(cls)
            cls._CONFIGS[filename] = instance
            return instance

    def __init__(self, filename, create=False,
                 template=GEOFFREY_CONFIG_TEMPLATE, read=True):
        self.filename = filename
        self.exists = os.path.isfile(filename)
        if not self.exists and create:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(template)
        super().__init__(default_section='geoffrey')
        if read:
            self.read()

    def getlist(self, section, option):
        try:
            return self[section][option].split(',')
        except:
            return None

    def read(self):
        super().read(self.filename)
