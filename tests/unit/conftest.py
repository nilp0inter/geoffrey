import pytest  # pragma: nocover

@pytest.fixture  # pragma: nocover
def loop():
    import asyncio
    loop = asyncio.get_event_loop()
    return loop


@pytest.fixture(scope='function')  # pragma: nocover
def hub(request):
    from geoffrey.hub import EventHUB
    hub = EventHUB()
    def fin():
        hub._drop()
    request.addfinalizer(fin)
    return hub


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
    import asyncio
    from geoffrey import plugin
    from geoffrey.subscription import subscription

    class StoreAllPlugin(plugin.GeoffreyPlugin):
        events_received = []

        @asyncio.coroutine
        def store_event(self, data: subscription()) -> plugin.Task:
            while True:
                item = yield from data.get()
                self.events_received.append(item)

    return StoreAllPlugin

