import pytest  # pragma: nocover

@pytest.fixture  # pragma: nocover
def loop():
    import asyncio
    loop = asyncio.get_event_loop()
    return loop


@pytest.fixture  # pragma: nocover
def hub():
    from geoffrey.hub import EventHUB
    return EventHUB(loop=loop())


@pytest.fixture  # pragma: nocover
def subscription():
    from geoffrey.subscription import Subscription
    return Subscription(loop=loop())


@pytest.fixture  # pragma: nocover
def event():
    from geoffrey.event import Event
    return Event()


@pytest.fixture  # pragma: nocover
def state():
    from geoffrey.state import State
    return State()


@pytest.fixture  # pragma: nocover
def storeallplugin():
    from geoffrey.plugin import GeoffreyPlugin
    from geoffrey.subscription import Subscription, ANYTHING

    class StoreAllPlugin(GeoffreyPlugin):
        def __init__(self, *args, **kwargs):
            self.events_received = []

            s = Subscription(loop())
            s.add_filter(ANYTHING)  # Allow all
            s.add_callback(self.store_event)
            self.subscriptions = [s]

            super().__init__(*args, **kwargs)

        def store_event(self, data):
            self.events_received.append(data)

    return StoreAllPlugin(None)

