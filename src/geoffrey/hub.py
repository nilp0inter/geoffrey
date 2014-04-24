import logging
import asyncio
import pickle

from .event import Event, EventType
from .state import State

logger = logging.getLogger(__name__)

class EventHUB:
    def __init__(self):
        self.events = asyncio.Queue()
        self.states = {}
        self.subscriptions = []
        asyncio.Task(self.run())

    def add_subscriptions(self, subscriptions):
        logger.debug("Adding subscriptions %r", subscriptions)
        self.subscriptions.extend(subscriptions)

    @asyncio.coroutine
    def run(self):
        while True:
            data = yield from self.events.get()
            logger.debug("Dispatching new event: %r", data)
            logger.debug("States: %r", self.states.keys())
            for subscription in self.subscriptions:
                yield from subscription.put(data)

    def set_state(self, data):
        self.states[data.key] = data.value

    def del_state(self, data):
        del self.states[data.key]

    @asyncio.coroutine
    def put(self, data):
        logger.debug("Received item: %r", data)
        if isinstance(data, Event):
            yield from self.events.put(data)
        elif isinstance(data, State):
            if data.key in self.states:  # Key already exists.
                if data.value:
                    if data.value != self.states[data.key]:
                        # Modified value
                        self.set_state(data)
                        ev = Event(type=EventType.modified, key=data.key,
                                   value=data.value)
                        yield from self.put(ev)
                    else:
                        # Same value.
                        # (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    self.del_state(data)
                    ev = Event(type=EventType.deleted, key=data.key)
                    yield from self.put(ev)
            elif data.value:
                # New value. Creation
                self.set_state(data)
                ev = Event(type=EventType.created, key=data.key,
                           value=data.value)
                yield from self.put(ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")

    def save_states(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.states, f)

    def restore_states(self, filename):
        with open(filename, 'rb') as f:
            self.states = pickle.load(f)
