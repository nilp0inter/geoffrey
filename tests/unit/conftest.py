import pytest  # pragma: nocover

@pytest.fixture  # pragma: nocover
def hub():
    from geoffrey.hub import EventHUB
    return EventHUB()


@pytest.fixture  # pragma: nocover
def event():
    from geoffrey.event import Event
    return Event()


@pytest.fixture  # pragma: nocover
def state():
    from geoffrey.state import State
    return State()
