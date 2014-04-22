from asyncio import Queue, coroutine

from .event import Event, EventType
from .state import State


class EventHUB:
    def __init__(self, loop):
        self.events = Queue(loop=loop)
        self.states = {}

    @coroutine
    def send(self, data):
        if isinstance(data, Event):
            yield from self.events.put(data)
        elif isinstance(data, State):
            if data.key in self.states:  # Key already exists.
                if data.value:  
                    if data.value != self.states[data.key]:
                        # Modified value
                        self.states[data.key] = data.value
                        ev = Event(type=EventType.modified, key=data.key,
                                   value=data.value)
                        yield from self.send(ev)
                    else:
                        # Same value.
                        # (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    del self.states[data.key]
                    ev = Event(type=EventType.deleted, key=data.key)
                    yield from self.send(ev)
            elif data.value:
                # New value. Creation
                self.states[data.key] = data.value
                ev = Event(type=EventType.created, key=data.key,
                           value=data.value)
                yield from self.send(ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")
