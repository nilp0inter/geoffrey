
class EventHUB:
    def __init__(self):
        self.events = []

    def send(self, data):
        self.events.append(data)
