

def test_state(state):
    assert state 


def test_state_key_and_value(state):
    from geoffrey.data import DataKey
    assert isinstance(state._key, DataKey)
    assert isinstance(state._value, dict)
