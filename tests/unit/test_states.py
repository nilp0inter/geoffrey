

def test_state(state):
    assert state 


def test_state_key_and_value(state):
    from geoffrey.state import StateKey
    assert isinstance(state.key, StateKey)
    assert isinstance(state.value, dict)
