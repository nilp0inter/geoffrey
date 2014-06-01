import asyncio
import pytest  # pragma: nocover

def setup_asyncio(function):
    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def teardown_asyncio(function):
    loop = asyncio.get_event_loop()
    try:
        loop.stop()
    except:  # pragma: no cover
        pass
    finally:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.close()

@pytest.fixture  # pragma: nocover
def loop(request):
    return asyncio.get_event_loop()


@pytest.fixture  # pragma: nocover
def hub(request):
    from geoffrey import hub
    def fin():
        hub._hub = None
    request.addfinalizer(fin)
    return hub.get_hub()


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
        def __init__(self, *args, stop_after=None, **kwargs):
            self.events_received = []
            self.stop_after = stop_after
            super().__init__(*args, **kwargs)

        @asyncio.coroutine
        def store_events(self, data: subscription()) -> plugin.Task:
            if self.stop_after is None:
                from itertools import count
                iterations = count()
            else:
                iterations = range(self.stop_after)

            for _ in iterations:
                item = yield from data.get()
                self.events_received.append(item)

    return StoreAllPlugin


@pytest.fixture
def testplugin():
    import asyncio
    from geoffrey import plugin
    from geoffrey.subscription import subscription

    sub = subscription(filter_func = lambda x: True)  # pragma: no cover

    class TestPlugin(plugin.GeoffreyPlugin):

        data = None

        @asyncio.coroutine
        def task1(self, mydata: sub) -> plugin.Task:
            self.data = yield from mydata.get()  # pragma: no cover

    return TestPlugin


@pytest.fixture
def consumer():
    from geoffrey.subscription import Consumer
    return Consumer()


@pytest.fixture
def wsserver():
    from geoffrey.subscription import Consumer
    from geoffrey.websocket import WebsocketServer
    con = Consumer()
    con.criteria = [{}]
    return WebsocketServer(consumers={'consumer': con})


@pytest.fixture
def websocket():
    def ws_factory(recv_data):
        class Websocket:
            """Mocket websocket"""
            def __init__(self):
                self._recv = asyncio.Queue()
                for d in recv_data:
                    self._recv.put_nowait(d)

                self._send = asyncio.Queue()

            @asyncio.coroutine
            def recv(self):
                return (yield from self._recv.get())

            @asyncio.coroutine
            def send(self, data):  # pragma: no cover
                return (yield from self._send.put(data))

        return Websocket

    return ws_factory


@pytest.fixture
def websocket_ready():
    import json
    from geoffrey.subscription import Consumer
    def ws_factory(recv_data):
        class Websocket:
            """Mocket websocket"""
            def __init__(self):
                self._recv = asyncio.Queue()
                for d in recv_data:
                    self._recv.put_nowait(d)

                self._send = asyncio.Queue()

            @asyncio.coroutine
            def recv(self):
                return (yield from self._recv.get())

            @asyncio.coroutine
            def send(self, data):
                return (yield from self._send.put(data))

        return Websocket
    tosend = [json.dumps({'consumer_id': 'consumer'})]
    ws = ws_factory(tosend)()
    return ws
