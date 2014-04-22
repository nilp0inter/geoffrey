import enum


class EventType(enum.Enum):
    unknown = None
    created = 1
    modified = 2
    deleted = 3


class Event:
    def __init__(self, type=EventType.unknown, key=None, value=None):
        self.type = type
        self.key = key
        self.value = value
