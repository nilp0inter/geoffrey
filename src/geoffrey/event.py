import enum
import json

from .state import StateKey

class EventType(enum.Enum):
    unknown = None
    created = 1
    modified = 2
    deleted = 3


_empty_key = StateKey(None, None, None)


class Event:
    def __init__(self, type=EventType.unknown, key=_empty_key, value=None):
        self.type = type
        self.key = key
        self.value = value

    def dumps(self):
        return json.dumps({
            'project': self.key.project,
            'plugin': self.key.plugin,
            'key': self.key.key,
            'value': self.value})

    def __str__(self):
        return '[{self.type}]{{{self.key}: {self.value}}}'.format(self=self)
