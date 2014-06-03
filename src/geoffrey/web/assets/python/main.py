from collections import deque
from collections import namedtuple
import json

from browser import ajax
from browser import alert
from browser import document as doc
from browser import timer
from browser import websocket

EventType = {
    'custom': None,
    'created': 1,
    'modified': 2,
    'deleted': 3,
    'state': 4
}

StateKey = namedtuple('StateKey', ('project', 'plugin', 'key'))
_empty_key = StateKey(None, None, None)
consumer_id = None
ws = None
hub = None

class Event:
    """Geoffrey event definition."""
    def __init__(self, type=EventType['custom'], key=_empty_key, value=None):
        self.type = type
        self.key = key
        self.value = value

    def serializable(self):
        return {'project': self.key.project,
                'plugin': self.key.plugin,
                'key': self.key.key,
                'value': self.value}

    def dumps(self):
        return json.dumps(self.serializable())

    def __str__(self):  # pragma: no cover
        return '[{self.type}]{{{self.key}: {self.value}}}'.format(
            self=self)


class State:
    """ Geoffrey State definition. """
    def __init__(self, **kwargs):
        self.key = StateKey(**{k:kwargs.get(k, None) for k in StateKey._fields})
        self.value = {k: kwargs.get(k)
                      for k in kwargs if k not in StateKey._fields}

    def __str__(self):  # pragma: no cover
        return '{{{self.key}: {self.value}}}'.format(self=self)


class Queue:
    def __init__(self, maxsize=None):
        self._queue = deque()

    def put(self, item):
        self._queue.append(item)

    def get(self):
        return self._queue.popleft()


class EventHUB:
    def __init__(self, *args, **kwargs):
        self.events = Queue()
        self.subscriptions = []
        self.running = True
        self.states = {}
        timer.set_timeout(self.run, 1000)
        print("Starting EventHUB!")

    def add_subscriptions(self, subscriptions):
        self.subscriptions.extend(subscriptions)

    def run(self):
        while True:
            try:
                data = self.events.get()
            except:
                timer.set_timeout(self.run, 1000)
                return
            else:
                print("Sending %s to %d subscriptions" % (data, len(self.subscriptions)))
                for subscription in self.subscriptions:
                    subscription.put(data)

    def _process_data(self, data):
        """
        Process the data received by the hub.

        Return a tuple (isfinal, event) => (bool, Event).

        """
        if isinstance(data, Event):
            #print("Event received: %s" % data)
            return (True, data)
        elif isinstance(data, State):
            #print("State received: %s" % data)
            if data.key in self.states:  # Key already exists.
                if data.value:
                    if data.value != self.states[data.key]:
                        # Modified value
                        self.set_state(data)
                        ev = Event(type=EventType['modified'], key=data.key,
                                   value=data.value)
                        return (False, ev)
                    else:
                        # Same value.
                        # (It's covered but coverage does not detect it.)
                        pass  # pragma: nocover
                else:
                    # No value means. Deletion.
                    self.del_state(data)
                    ev = Event(type=EventType['deleted'], key=data.key)
                    return (False, ev)
            elif data.value:
                # New value. Creation
                self.set_state(data)
                ev = Event(type=EventType['created'], key=data.key,
                           value=data.value)
                return (False, ev)
            else:
                # No value means. Deletion. But is an unknown key.
                # (It's covered but coverage does not detect it.)
                pass  # pragma: nocover
        else:
            raise TypeError("Unknown data type.")

        return (None, None)

    def put(self, data):
        """
        Put a state or event in the hub.

        This method is NOT a coroutine, use::

            hub.put_nowait(data)

        """
        isfinal, event = self._process_data(data)
        if event is not None:
            if isfinal:
                self.events.put(event)
            else:
                self.put(event)

    def set_state(self, data):
        """Set a state in the hub state table."""
        self.states[data.key] = data.value

    def del_state(self, data):
        """Delete a state of the hub state table."""
        del self.states[data.key]


#
# CONNECT TO WS
#
def on_open(evt):
    ws.send(json.dumps({"consumer_id": consumer_id}))

def on_message(evt):
    # message reeived from server
    payload = json.loads(evt.data)
    value = payload.pop("value")
    state = State(**payload)
    state.value = value
    doc["output"].append("<pre>" + evt.data + "</pre><br/>")
    #hub.put(state)

def on_close(evt):
    # websocket is closed
    alert("Connection is closed")

def _open(ev):
    if not __BRYTHON__.has_websocket:
        alert("WebSocket is not supported by your browser")
        return
    global ws
    # open a web socket
    ws = websocket.websocket("ws://127.0.0.1:8701")
    # bind functions to web socket events
    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)

def send(ev):
    data = doc["data"].value
    if data:
        ws.send(data)

def close_connection(ev):
    ws.close()
    doc['openbtn'].disabled = False

#
# REGISTER THE CONSUMER
#
def on_subscription_complete(req):
    if req.status==200 or req.status==0:
        pass
    else:
        alert("subscription complete ERROR")

def on_consumer_complete(req):
    global consumer_id
    if req.status==200 or req.status==0:
        consumer_id = json.loads(req.text).get("id")

        # Connect to WS
        _open(None)

        # Make subscription
        url = "http://localhost:8700/api/v1/subscription/" + consumer_id
        req2 = ajax.ajax()
        req2.bind('complete', on_subscription_complete)
        req2.open('POST', url, True)
        req2.set_header('content-type','application/json')
        req2.send({"criteria": """[{'plugin': 'testpylint'}]"""})
    else:
        alert("Error registering consumer")

def start_client():
    # Create the event hub
    global hub
    hub = EventHUB()

    # Register this consumer
    url = "http://localhost:8700/api/v1/consumer"
    req = ajax.ajax()
    req.bind('complete', on_consumer_complete)
    req.open('POST', url, True)
    req.set_header('content-type','application/json')
    req.send()

if __name__ == '__main__':
    start_client()
