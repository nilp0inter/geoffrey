import asyncio
import logging
import pickle

from .event import Event, EventType
from .state import State

# Global, implicit hub
_hub = None

logger = logging.getLogger(__name__)


class EventHUB:
    """The main data exchanger."""
    instance = None

    def __init__(self, *args, **kwargs):
        self.events = asyncio.Queue()
        self.subscriptions = []
        self.running = False
        self.states = {}

    def add_subscriptions(self, subscriptions):
        self.subscriptions.extend(subscriptions)

    @asyncio.coroutine
    def run(self):
        logger.debug("Starting EventHUB!")
        if not self.running:
            self.running = True
        else:
            raise RuntimeError("HUB run method can't be exec twice.")

        while True:
            try:
                data = self.events.get_nowait()
            except:
                yield from asyncio.sleep(1)
            else:
                logger.debug("Sending %s to %d subscriptions",
                             data, len(self.subscriptions))
                for subscription in self.subscriptions:
                    yield from subscription.put(data)

    def set_state(self, data):
        self.states[data.key] = data.value

    def del_state(self, data):
        del self.states[data.key]

    def _process_data(self, data):
        """Return a tuple (isfinal, event) => (bool, Event)"""
        if isinstance(data, Event):
            logger.debug("Event received: %s", data)
            return (True, data)
        elif isinstance(data, State):
            logger.debug("State received: %s", data)
            if data.key in self.states:  # Key already exists.
                if data.value:
                    if data.value != self.states[data.key]:
                        # Modified value
                        self.set_state(data)
                        ev = Event(type=EventType.modified, key=data.key,
                                   value=data.value)
                        return (False, ev)
                    else:
                        # Same value.
                        # (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    self.del_state(data)
                    ev = Event(type=EventType.deleted, key=data.key)
                    return (False, ev)
            elif data.value:
                # New value. Creation
                self.set_state(data)
                ev = Event(type=EventType.created, key=data.key,
                           value=data.value)
                return (False, ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")

        return (None, None)

    @asyncio.coroutine
    def put(self, data):
        """
        Put a state or event in the hub.

        This method is a coroutine, use::

            yield from hub.put(data)

        """
        isfinal, event = self._process_data(data)
        if event is not None:
            if isfinal:
                yield from self.events.put(event)
            else:
                yield from self.put(event)

    def put_nowait(self, data):
        """
        Put a state or event in the hub.

        This method is NOT a coroutine, use::

            hub.put_nowait(data)

        """
        isfinal, event = self._process_data(data)
        if event is not None:
            if isfinal:
                self.events.put_nowait(event)
            else:
                self.put_nowait(event)

    def save_states(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.states, f)

    def restore_states(self, filename):
        with open(filename, 'rb') as f:
            self.states = pickle.load(f)


def get_hub():
    """Return the global event hub."""
    global _hub
    if _hub is None:
        _hub = EventHUB()
    return _hub
