import os
import configparser

from geoffrey import default

GEOFFREY_CONFIG_TEMPLATE = """[geoffrey]
host={default.HOST}
webserver_port={default.WEBSERVER_PORT}
websocket_port={default.WEBSOCKET_PORT}
""".format(default=default)


class Config(configparser.ConfigParser):
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

    def read(self):
        super().read(self.filename)
