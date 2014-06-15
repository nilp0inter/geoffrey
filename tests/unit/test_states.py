import pytest

def test_state(state):
    assert state 


def test_state_key_and_value(state):
    from geoffrey.data import DataKey
    assert isinstance(state._key, DataKey)
    assert isinstance(state._value, dict)


def test_data_getattr():
    from geoffrey import data
    state = data.State(key="key", other="other")

    assert state.key == "key"
    assert state.other == "other"
    assert state.unknown is None
