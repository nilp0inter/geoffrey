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


def test_new_state_created_event(hub):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state = State(object='testobject', value='something interesting')

    assert len(hub.events) == 0
    hub.send(state)
    assert len(hub.events) == 1

    assert hub.events.pop().type == EventType.created
    assert state.key in hub.states


def test_modified_state_modified_event(hub):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(object='testobject', value='something interesting')

    hub.send(state1)
    assert hub.events.pop().type == EventType.created
    assert state1.key in hub.states

    state2 = State(object='testobject', value='different stuff')

    hub.send(state2)
    assert hub.events.pop().type == EventType.modified
    assert state2.key in hub.states


def test_same_state_do_nothing(hub):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = state2 = State(object='testobject', value='something interesting')

    hub.send(state1)
    assert hub.events.pop().type == EventType.created
    assert state1.key in hub.states

    hub.send(state2)
    assert len(hub.events) == 0
    assert state2.key in hub.states


def test_empty_state_means_deletion(hub):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(object='testobject', value='something interesting')

    hub.send(state1)
    assert hub.events.pop().type == EventType.created
    assert state1.key in hub.states

    state2 = State(object='testobject')

    hub.send(state2)
    assert hub.events.pop().type == EventType.deleted
    assert not state2.key in hub.states
