import pytest

@pytest.fixture
def hub():
    from geoffrey.hub import EventHUB
    return EventHUB()


@pytest.fixture
def event():
    from geoffrey.event import Event
    return Event()


@pytest.fixture
def state():
    from geoffrey.state import State
    return State()
