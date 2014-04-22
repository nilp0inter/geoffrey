import pytest

def test_hub(hub):
    assert hub


def test_send_event(hub, event, loop):
    assert hub.events.qsize() == 0
    loop.run_until_complete(hub.send(event))
    assert hub.events.qsize() == 1
    ret_event = loop.run_until_complete(hub.events.get())
    assert event == ret_event


def test_send_state(hub, state, loop):
    assert hub.events.qsize() == 0
    loop.run_until_complete(hub.send(state))
    assert hub.events.qsize() == 0


def test_cant_send_garbage(hub, loop):
    with pytest.raises(TypeError):
        loop.run_until_complete(hub.send("nothing"))


def test_new_state_created_event(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state = State(object='testobject', value='something interesting')


    loop.run_until_complete(hub.send(state))
    event = loop.run_until_complete(hub.events.get())
    assert event.type == EventType.created
    assert state.key in hub.states


def test_modified_state_modified_event(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(object='testobject', value='something interesting')

    loop.run_until_complete(hub.send(state1))
    ev1 = loop.run_until_complete(hub.events.get())
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    state2 = State(object='testobject', value='different stuff')

    loop.run_until_complete(hub.send(state2))
    ev2 = loop.run_until_complete(hub.events.get())
    assert ev2.type == EventType.modified
    assert state2.key in hub.states


def test_same_state_do_nothing(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = state2 = State(object='testobject', value='something interesting')

    loop.run_until_complete(hub.send(state1))
    ev1 = loop.run_until_complete(hub.events.get())
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    loop.run_until_complete(hub.send(state2))
    assert hub.events.qsize() == 0
    assert state2.key in hub.states


def test_empty_state_means_deletion(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(object='testobject', value='something interesting')

    loop.run_until_complete(hub.send(state1))
    ev1 = loop.run_until_complete(hub.events.get())
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    state2 = State(object='testobject')

    loop.run_until_complete(hub.send(state2))
    ev2 = loop.run_until_complete(hub.events.get())
    assert ev2.type == EventType.deleted
    assert not state2.key in hub.states
