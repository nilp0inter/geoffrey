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
