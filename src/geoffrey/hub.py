"""
The EventHUB and related functions..

"""
#pylint: disable=I0011, E1101, W0212, W0603, C0103
from asyncio.queues import QueueFull
import asyncio
import logging
import pickle

from geoffrey.data import State, Event, EventType

# Global, implicit hub
_hub = None

logger = logging.getLogger(__name__)


class EventHUB:
    """The main data exchanger."""
    instance = None

    def __init__(self):
        self.events = asyncio.Queue()
        self.subscriptions = []
        self.running = False
        self.states = {}

    def add_subscriptions(self, subscriptions):
        """Extend the subscription list with the given `subscriptions`."""
        self.subscriptions.extend(subscriptions)

    def get_states(self, key_criteria):
        """Generator with the matching states of the key_criteria."""
        for key, value in self.states.items():
            for field in key_criteria._fields:
                expected = getattr(key_criteria, field)
                if expected is None:  # expected=None means I don't care
                    continue

                current = getattr(key, field)
                if current != expected:
                    break
            else:
                # Everything right. <zeusvoice>RELEASE THE STATE!!</zeusvoice>
                yield State.from_keyvalue(key, value)

    def get_one_state(self, key_criteria):
        """Like get_states but return the first matching state or None."""
        try:
            return next(self.get_states(key_criteria))
        except StopIteration:
            return None

    @asyncio.coroutine
    def run(self):
        """Infite loop that send events to the subscribers."""
        logger.debug("Starting EventHUB!")
        if not self.running:
            self.running = True
        else:
            raise RuntimeError("HUB run method can't be exec twice.")

        while True:
            data = yield from self.events.get()
            logger.debug("Sending %s to %d subscriptions",
                         data, len(self.subscriptions))
            for subscription in self.subscriptions:
                try:
                    subscription.put_nowait(data)
                except QueueFull:
                    pass

    def _process_state(self, state, force_change):
        """
        Process the given `state` and produce events according to the
        rules.

        """
        logger.debug("State received: %s", state)
        key, value = state.to_keyvalue()
        if key in self.states:  # Key already exists.
            if value:
                if value != self.states[key] or force_change:
                    # Modified value
                    self.states[key] = value
                    event = state.to_event(EventType.modified)
                    return (False, event)
                else:
                    # Same value.
                    # (It's covered but coverage does not detect it.)
                    return (None, None) # pragma: nocover
            else:
                # No value means deletion.
                del self.states[key]
                event = Event.from_keyvalue(key, None,
                                            type=EventType.deleted)
                return (False, event)
        elif value:
            # New value. Creation
            self.states[key] = value
            event = state.to_event(type=EventType.created)
            return (False, event)
        else:
            # No value means. Deletion. But is an unknown key.
            # (It's covered but coverage does not detect it.)
            return (None, None) # pragma: nocover

    def _process_data(self, data, force_change):
        """
        Process the data received by the hub.

        Return a tuple (isfinal, event) => (bool, Event).

        """
        if isinstance(data, Event):
            return (True, data)
        elif isinstance(data, State):
            return self._process_state(data, force_change=force_change)
        else:
            raise TypeError("Unknown data type.")

    @asyncio.coroutine
    def put(self, data, force_change=False):
        """
        Put a state or event in the hub.

        This method is a coroutine, use::

            yield from hub.put(data)

        """
        isfinal, event = self._process_data(data, force_change=force_change)
        if event is not None:
            if isfinal:
                yield from self.events.put(event)
            else:
                yield from self.put(event, force_change=force_change)

    def put_nowait(self, data, force_change=False):
        """
        Put a state or event in the hub.

        This method is NOT a coroutine, use::

            hub.put_nowait(data)

        """
        isfinal, event = self._process_data(data, force_change=force_change)
        if event is not None:
            if isfinal:
                self.events.put_nowait(event)
            else:
                self.put_nowait(event, force_change=force_change)

    def save_states(self, filename):
        """Save the state table to disk."""
        with open(filename, 'wb') as outputfile:
            pickle.dump(self.states, outputfile)

    def restore_states(self, filename):
        """Load the state table from disk."""
        with open(filename, 'rb') as inputfile:
            self.states = pickle.load(inputfile)


def get_hub():
    """Return the global event hub."""
    global _hub
    if _hub is None:
        _hub = EventHUB()
    return _hub
