import asyncio
import configparser

import pytest

from geoffrey import plugin
from geoffrey.plugins.dummy import DummyPlugin


def test_plugin_load(hub):
    config = configparser.ConfigParser()
    config.add_section('plugin:DummyPlugin')
    plugin_list = plugin.get_plugins(config, hub)
    assert any([isinstance(p, DummyPlugin) for p in plugin_list])


def test_plugin_found_tasks():
    class TestPlugin(plugin.GeoffreyPlugin):  # pragma: no cover
        def nothing_interesting(self):
            pass

        def nothing_interesting2(self) -> 'nothing':
            pass

        @asyncio.coroutine
        def task1(self) -> plugin.Task:
            yield from asyncio.sleep(1)

        @asyncio.coroutine
        def task2(self) -> plugin.Task:
            yield from asyncio.sleep(1)

    tasks = TestPlugin.get_tasks()
    assert TestPlugin.task1 in tasks
    assert TestPlugin.task2 in tasks
    assert len(tasks) == 2


def test_plugin_found_subscriptions(hub):
    from geoffrey.subscription import subscription, _Subscription
    sub = subscription()
    class TestPlugin(plugin.GeoffreyPlugin):
        @asyncio.coroutine
        def task1(self, mydata: sub) -> plugin.Task:
            yield from asyncio.sleep(1)

    p = TestPlugin(config=None, hub=hub)

    assert len(p.subscriptions) == 1
    assert isinstance(p.subscriptions[0], _Subscription)


def test_plugin_start_tasks_on_init(hub, loop, event):
    from geoffrey.subscription import subscription

    sub = subscription(filter_func = lambda x: True)

    class TestPlugin(plugin.GeoffreyPlugin):

        data = None

        @asyncio.coroutine
        def task1(self, mydata: sub) -> plugin.Task:
            self.data = yield from mydata.get()

    @asyncio.coroutine
    def queue_event():
        yield from hub.put(event)
        yield from asyncio.sleep(1)

    p = TestPlugin(config=None, hub=hub)
    hub.add_subscriptions(p.subscriptions)
    loop.run_until_complete(asyncio.wait([hub.run(), queue_event()],
                                         return_when=asyncio.FIRST_COMPLETED))
    assert p.data == event


def test_plugin_subscription(storeallplugin, hub, event, loop):

   storeallplugin = storeallplugin(config=None, hub=hub)
   hub.add_subscriptions(storeallplugin.subscriptions)

   loop.run_until_complete(hub.put(event))
   assert hub.events.qsize() == 1

   loop.run_until_complete(
       asyncio.wait([hub.run(), asyncio.sleep(1)],
                    return_when=asyncio.FIRST_COMPLETED))

   assert event in storeallplugin.events_received
