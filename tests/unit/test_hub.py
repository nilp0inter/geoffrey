import pytest

def test_hub(hub):
    assert hub


def test_send_event(hub, event):
    hub.send(event)
    assert event in hub.events


def test_send_state(hub, state):
    hub.send(state)
    assert state not in hub.events


def test_cant_send_garbage(hub):
    with pytest.raises(TypeError):
        hub.send("nothing")
