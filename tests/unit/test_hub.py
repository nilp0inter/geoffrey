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
    from geoffrey.data import State
    from geoffrey.data import EventType

    state = State(key='testobject', value='something interesting')


    loop.run_until_complete(hub.put(state))
    event = hub.events.get_nowait()
    assert event.type == EventType.created
    assert state._key in hub.states


def test_modified_state_modified_event(hub, loop):
    from geoffrey.data import State
    from geoffrey.data import EventType

    state1 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1._key in hub.states

    state2 = State(key='testobject', value='different stuff')

    loop.run_until_complete(hub.put(state2))
    ev2 = hub.events.get_nowait()
    assert ev2.type == EventType.modified
    assert state2._key in hub.states


def test_same_state_do_nothing(hub, loop):
    from geoffrey.data import State
    from geoffrey.data import EventType

    state1 = state2 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1._key in hub.states

    loop.run_until_complete(hub.put(state2))
    assert hub.events.qsize() == 0
    assert state2._key in hub.states


def test_empty_state_means_deletion(hub, loop):
    from geoffrey.data import State
    from geoffrey.data import EventType

    state1 = State(key='testobject', value='something interesting')

    loop.run_until_complete(hub.put(state1))
    ev1 = hub.events.get_nowait()
    assert ev1.type == EventType.created
    assert state1._key in hub.states

    state2 = State(key='testobject')

    loop.run_until_complete(hub.put(state2))
    ev2 = hub.events.get_nowait()
    assert ev2.type == EventType.deleted
    assert not state2._key in hub.states


def test_states_persistence(hub):
    from tempfile import NamedTemporaryFile 
    from geoffrey.data import State

    state1 = State(key='object1', data='data')
    hub.set_state(state1)
    state2 = State(key='object2', data='data')
    hub.set_state(state2)

    with NamedTemporaryFile() as tf:
        hub.save_states(tf.name)
        hub.state = {}
        hub.restore_states(tf.name)

    assert state1._key in hub.states
    assert state2._key in hub.states


def test_hub_is_global():
    from geoffrey.hub import get_hub
    hub1 = get_hub()
    hub2 = get_hub()
    assert hub1 is hub2


def test_hub_cant_run_twice(hub, loop):
    import asyncio
    tasks = asyncio.wait([hub.run(), hub.run()],
                         return_when=asyncio.FIRST_COMPLETED)
    done, pending = loop.run_until_complete(tasks)

    tdone = list(done)
    tpending = list(pending)

    assert len(tdone) == 1
    assert len(tpending) == 1

    with pytest.raises(RuntimeError):
        tdone[0].result()


def test_hub_put_nowait(hub, event):
    assert hub.events.qsize() == 0
    hub.put_nowait(event)
    assert hub.events.qsize() == 1
    ret_event = hub.events.get_nowait()
    assert event == ret_event


def test_put_nowait_state(hub, state, loop):
    assert hub.events.qsize() == 0
    hub.put_nowait(state)
    assert hub.events.qsize() == 0


def test_new_state_created_event_put_nowait(hub, loop):
    from geoffrey.data import State
    from geoffrey.data import EventType

    state = State(key='testobject', value='something interesting')

    hub.put_nowait(state)
    event = hub.events.get_nowait()
    assert event.type == EventType.created
    assert state._key in hub.states


def test_get_states_nomatch(hub):
    from geoffrey.data import State, DataKey

    state1 = State(key='badkey', value='something')
    hub.put_nowait(state1)

    states = list(hub.get_states(DataKey(project=None,
                                          plugin=None,
                                          key='goodkey')))

    assert states == []


def test_get_states_match_single_field(hub):
    from geoffrey.data import State, DataKey
    from geoffrey.data import EventType

    state1 = State(key='goodkey', value='something')
    hub.put_nowait(state1)

    states = list(hub.get_states(DataKey(project=None,
                                          plugin=None,
                                          key='goodkey')))

    assert len(states) == 1
    assert states[0]._key == state1._key
    assert states[0]._value == state1._value


def test_get_states_match_multiple_fields(hub):
    from geoffrey.data import State, DataKey
    from geoffrey.data import EventType

    state1 = State(project='goodproject', key='goodkey', value='something')
    hub.put_nowait(state1)

    states = list(hub.get_states(DataKey(project='goodproject',
                                          plugin=None,
                                          key='goodkey')))

    assert len(states) == 1
    assert states[0]._key == state1._key
    assert states[0]._value == state1._value


def test_get_states_match_mixed(hub):
    from geoffrey.data import State, DataKey
    from geoffrey.data import EventType

    state1 = State(project='goodproject', key='goodkey', value='something')
    hub.put_nowait(state1)

    state2 = State(project='badproject', key='goodkey', value='something')
    hub.put_nowait(state2)

    states = list(hub.get_states(DataKey(project='goodproject',
                                          plugin=None,
                                          key='goodkey')))

    assert len(states) == 1
    assert states[0]._key == state1._key
    assert states[0]._value == state1._value
