import enum
import json

from .state import StateKey

class EventType(enum.Enum):
    #: A custom event.
    custom = None

    #: An event is generated because an state is created in the hub.
    created = 1

    #: An event is generated because an state is modified in the hub.
    modified = 2

    #: An event is generated because an state is deleted in the hub.
    deleted = 3

    #: Used when someone query the states of the hub.
    state = 4


_empty_key = StateKey(None, None, None)


class Event:
    def __init__(self, type=EventType.custom, key=_empty_key, value=None):
        self.type = type
        self.key = key
        self.value = value

    def serializable(self):
        return {'project': self.key.project,
                'plugin': self.key.plugin,
                'key': self.key.key,
                'value': self.value}

    def dumps(self):
        return json.dumps(self.serializable())

    def __str__(self):  # pragma: no cover
        return '[{self.type}]{{{self.key}: {self.value}}}'.format(self=self)
