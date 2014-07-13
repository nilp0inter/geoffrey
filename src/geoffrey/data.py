#pylint: disable=E1101,E1103,W0212,W0622,W0232,W0142
import enum

from collections import namedtuple
from itertools import zip_longest


DataKey = namedtuple('DataKey',
                     ('project',
                      'plugin',         # The plugin that generate this data.
                      'key',            # The subject thing
                      'task',           # The task that generate this data.
                      'content_type'))  # Is this data following some
                                        # convention?


def datakey(*args, **kwargs):
    """Helper function for build DataKey tuples."""
    newargs = [kwargs.get(k, v)
               for k, v in zip_longest(DataKey._fields, args)]
    return DataKey(*newargs)

_EMPTY_KEY = datakey()


class EventType(enum.Enum):
    """The possible types of an event."""

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


class Data:
    """ Geoffrey Data definition. """

    def __init__(self, **kwargs):
        self._key = DataKey(*(kwargs.get(k, None)
                             for k in DataKey._fields))
        self._value = {k: kwargs.get(k)
                        for k in kwargs
                        if k not in DataKey._fields}

    def __getattr__(self, name):
        if name in self._key._fields:
            return getattr(self._key, name)
        else:
            if name in self._value:
                return self._value[name]
            else:
                return None

    def __str__(self):  # pragma: no cover
        return '{{{self._key}: {self._value}}}'.format(self=self)

    def serializable(self):
        dump = {k:getattr(self, k) for k in DataKey._fields}
        dump['value'] = self._value
        return dump

    def dumps(self):
        from geoffrey.utils import jsonencoder
        return jsonencoder.encode(self.serializable())

    def to_keyvalue(self):
        return (self._key, self._value)

    @classmethod
    def from_keyvalue(cls, key, value=None, **kwargs):
        self = cls()
        self._key = key
        if value is None:
            self._value = {}
        else:
            self._value = value
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self


class Event(Data):
    """Geoffrey event definition."""
    def __init__(self, *args, type=EventType.custom, **kwargs):
        self.type = type
        super().__init__(*args, **kwargs)

    def __str__(self):  # pragma: no cover
        return '[{self.type}]{{{self._key}: {self._value}}}'.format(
            self=self)

    def serializable(self):
        dump = super().serializable()
        dump['type'] = self.type.name
        return dump

    @classmethod
    def from_data(cls, data, type):
        self = cls(type=type)
        self._key = data._key
        self._value = data._value
        return self


class State(Data):
    """ Geoffrey State definition. """
    def to_event(self, type):
        return Event.from_data(self, type)
