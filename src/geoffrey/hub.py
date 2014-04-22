from .event import Event
from .state import State


class EventHUB:
    def __init__(self):
        self.events = []

    def send(self, data):
        if isinstance(data, Event):
            self.events.append(data)
        elif isinstance(data, State):
            # TODO: Emit events as neccesary.
            #       Save state.
            pass
        else:
            raise TypeError("Unknown data type.")
