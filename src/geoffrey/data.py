"""
"""
import json
import base64


class Data:
    def __init__(self, data):
        self._data = data

    def dump(self):
        payload = {'type': self.__class__.__name__, 'content': self.render()}
        return json.dumps(payload)

    def render(self):
        raise NotImplementedError


class Text(Data):
    def render(self):
        return self._data


class HTML(Text):
    pass


class Image(Data):
    def render(self):
        return 'data:image/png;base64,' + base64.b64encode(self._data).decode('ascii')
