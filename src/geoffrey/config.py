import os
import configparser

GEOFFREY_CONFIG_TEMPLATE = """[geoffrey]
host=127.0.0.1
webserver_port=8555
websocket_port=8556

"""


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
