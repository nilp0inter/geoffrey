import pytest

def test_hub(hub):
    assert hub


def test_put_event(hub, event, loop):
    assert hub.events.qsize() == 0
    loop.run_until_complete(hub.put(event))
    assert hub.events.qsize() == 1
    ret_event = hub.events.get_nowait()
    assert event == ret_event


def test_put_state(hub, state, loop):
    assert hub.events.qsize() == 0
    loop.run_until_complete(hub.put(state))
    assert hub.events.qsize() == 0


def test_cant_put_garbage(hub, loop):
    with pytest.raises(TypeError):
        loop.run_until_complete(hub.put("nothing"))


def test_new_state_created_event(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state = State(key='testobject', value='something interesting')


    loop.run_until_complete(hub.put(state))
    event = hub.events.get_nowait()
    assert event.type == EventType.created
    assert state.key in hub.states


def test_modified_state_modified_event(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    state2 = State(key='testobject', value='different stuff')

    loop.run_until_complete(hub.put(state2))
    ev2 = hub.events.get_nowait()
    assert ev2.type == EventType.modified
    assert state2.key in hub.states


def test_same_state_do_nothing(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = state2 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    loop.run_until_complete(hub.put(state2))
    assert hub.events.qsize() == 0
    assert state2.key in hub.states


def test_empty_state_means_deletion(hub, loop):
    from geoffrey.state import State
    from geoffrey.event import EventType

    state1 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1.key in hub.states

    state2 = State(key='testobject')

    loop.run_until_complete(hub.put(state2))
    ev2 = hub.events.get_nowait()
    assert ev2.type == EventType.deleted
    assert not state2.key in hub.states


def test_states_persistence(hub):
    from tempfile import NamedTemporaryFile 
    from geoffrey.state import State

    state1 = State(key='object1', data='data')
    hub.set_state(state1)
    state2 = State(key='object2', data='data')
    hub.set_state(state2)

    with NamedTemporaryFile() as tf:
        hub.save_states(tf.name)
        hub.state = {}
        hub.restore_states(tf.name)

    assert state1.key in hub.states
    assert state2.key in hub.states


def test_hub_is_singleton():
    from geoffrey.hub import EventHUB
    hub1 = EventHUB()
    hub2 = EventHUB()
    assert hub1 is hub2
