import asyncio

from .event import Event, EventType
from .state import State


class EventHUB:
    def __init__(self, loop):
        self.events = asyncio.Queue(loop=loop)
        self.states = {}
        self.subscriptions = []
        self.active = True
        self._run_once = False

    def add_subscriptions(self, subscriptions):
        self.subscriptions.extend(subscriptions)

    def subscription_tasks(self):
        return [s.run() for s in self.subscriptions]


    @asyncio.coroutine
    def publish(self):
        while self.active:
            data = yield from self.events.get()
            for subscription in self.subscriptions:
                yield from subscription.put(data)
            if self._run_once:
                break

    @asyncio.coroutine
    def run(self):
        yield from asyncio.wait(
            [self.publish()] + self.subscription_tasks())

    @asyncio.coroutine
    def put(self, data):
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
                        yield from self.put(ev)
                    else:
                        # Same value.
                        # (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    del self.states[data.key]
                    ev = Event(type=EventType.deleted, key=data.key)
                    yield from self.put(ev)
            elif data.value:
                # New value. Creation
                self.states[data.key] = data.value
                ev = Event(type=EventType.created, key=data.key,
                           value=data.value)
                yield from self.put(ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")
