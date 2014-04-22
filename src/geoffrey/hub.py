from .event import Event, EventType
from .state import State


class EventHUB:
    def __init__(self):
        self.events = []
        self.states = {}

    def send(self, data):
        if isinstance(data, Event):
            self.events.append(data)
        elif isinstance(data, State):
            if data.key in self.states:  # Key already exists.
                if data.value:  
                    if data.value != self.states[data.key]:
                        # Modified value
                        self.states[data.key] = data.value
                        ev = Event(type=EventType.modified, key=data.key, value=data.value)
                        self.send(ev)
                    else:
                        # Same value. (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    del self.states[data.key]
                    ev = Event(type=EventType.deleted, key=data.key)
                    self.send(ev)
            elif data.value:
                # New value. Creation
                self.states[data.key] = data.value
                ev = Event(type=EventType.created, key=data.key, value=data.value)
                self.send(ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")
