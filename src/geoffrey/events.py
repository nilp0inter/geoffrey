from pyinotify import EventsCodes
import json
import getpass
from datetime import datetime
import socket
from enum import Enum
from .namespace import Namespace

EVENTS = EventsCodes.ALL_FLAGS

NOW = '__NOW__'


class EventType(Enum):
    created = "created"
    deleted = "deleted"
    changed = "changed"
    discovered = "discovered"
    status = "status"


class Event:
    def __init__(self, timestamp=None, hostname=socket.gethostname(),
                 username=getpass.getuser(), namespace=None, object_=None,
                 type_=None, source=None, data=None, events=None):

        if timestamp == NOW:
            self.timestamp = datetime.today()
        else:
            self.timestamp = timestamp

        self.hostname = hostname
        self.username = username

        if namespace is not None and not namespace in Namespace:
            raise TypeError('namespace must belong to Namespace()')
        else:
            self.namespace = namespace

        self.object = object_

        if type_ is not None and not type_ in EventType:
            raise TypeError('type_ must belong to EventType()')
        else:
            self.type = type_

        self.source = source
        self.data = data
        self.events = events

    def dump(self, *args, **kwargs):
        def get_attr(key, trans=lambda x: x):
            if getattr(self, key, None) is None:
                return {}
            else:
                return {key: trans(getattr(self, key))}

        data = {}
        data.update(get_attr('timestamp',
                             lambda x: float(x.strftime('%s.%f'))))
        data.update(get_attr('hostname'))
        data.update(get_attr('username'))
        data.update(get_attr('namespace', lambda x: x.value))
        data.update(get_attr('object'))
        data.update(get_attr('type', lambda x: x.value))
        data.update(get_attr('source'))
        data.update(get_attr('data'))
        data.update(get_attr('events'))

        return json.dumps(data, *args, **kwargs)

    def __repr__(self):
        return self.dump(sort_keys=True, indent=2)
