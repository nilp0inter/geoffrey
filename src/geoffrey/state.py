from collections import namedtuple


StateKey = namedtuple('StateKey', ('project', 'plugin', 'key'))


class State:
    def __init__(self, **kwargs):
        self.key = StateKey(*(kwargs.get(k, None) for k in StateKey._fields))
        self.value = {k: kwargs.get(k)
                      for k in kwargs if k not in StateKey._fields}
