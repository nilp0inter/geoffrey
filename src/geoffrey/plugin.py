import os
import asyncio
from asyncio import subprocess
from fnmatch import fnmatchcase
from collections import defaultdict

from straight.plugin import load
from straight.plugin.manager import PluginManager

from geoffrey.events import EVENTS
from functools import reduce
from operator import or_


class EventManager:
    def __init__(self):
        self.subscriptions = defaultdict(list)

    def get_mask(self):
        """
        Get event mask from subscriptions.

        """
        return reduce(or_, self.subscriptions.keys())

    def add_subscriptions(self, subscriptions):
        for subscription in subscriptions:
            self.subscriptions[subscription.event].append(subscription)

    @asyncio.coroutine
    def consume_events(self, queue, output):

        def done(future):
            yield from output.put(future.result())

        while True:
            event = yield from queue.get()
            event_id = event.mask
            filename = os.path.join(event.path, event.name)
            if event_id in self.subscriptions:
                for subscription in self.subscriptions[event_id]:
                    if subscription.match(filename):
                        future_output = subscription.who.process_file(filename)
                        if future_output:
                            future_output.add_done_callback(done)


class Subscription:
    def __init__(self, who, event, what):
        #: Subscribed plugin
        self.who = who

        #: PyInotify event
        self.event = event

        #: Fnmatch file expresion
        self.match = lambda f: fnmatchcase(f, what)


@asyncio.coroutine
def getstatusoutput(*args):
    """
    Devuelve el resultado de la ejecución de un comando.

    """
    proc = yield from asyncio.create_subprocess_exec(*args,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.STDOUT)
    try:
        stdout, stderr = yield from proc.communicate()
    except:
        proc.kill()
        yield from proc.wait()
        raise
    exitcode = yield from proc.wait()
    return (exitcode, stdout, stderr)


class GeoffreyPlugin:
    """
    Base plugin.

    """
    section = None

    def __init__(self, config, output_queue):
        self.config = config
        self.output_queue = output_queue

    def process_file(self, filename):
        return asyncio.async(self.run(filename))

    @property
    def plugin_name(self):
        if self.section is None:
            return self.__class__.__name__.lower()
        else:
            return self.section

    @property
    def section_name(self):
        return 'plugin:' + self.plugin_name

    def is_enabled(self):
        return self.section_name in self.config.sections()

    def get_subscriptions(self):
        subscriptions = []
        for event_name, event_id in EVENTS.items():
            file_exps = self.config.getlist(self.section_name, event_name)
            if file_exps:
                for file_exp in file_exps:
                    subscriptions.append(
                        Subscription(who=self, event=event_id, what=file_exp))
        return subscriptions

    @asyncio.coroutine
    def run(self, filename):
        raise NotImplementedError


def get_plugins(*args, **kwargs):
    all_plugins = load('geoffrey.plugins',
                       subclasses=GeoffreyPlugin).produce(*args, **kwargs)
    return PluginManager(list(filter(lambda p: p.is_enabled(), all_plugins)))

if __name__ == '__main__':
    from geoffrey import config
    c = config.Config('/home/nil/.geoffreyrc', create=True)
    p = get_plugins(c)

    from geoffrey import config
    c = config.Config('/home/nil/.geoffreyrc', create=True)

    from geoffrey.plugin import get_plugins
    p = get_plugins(c)
    p.call('is_enabled')
    list(p.call('get_subscriptions'))
