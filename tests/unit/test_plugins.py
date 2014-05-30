from tempfile import TemporaryDirectory
import os
import asyncio
import configparser

import pytest

from geoffrey import plugin
from geoffrey.plugins.dummy import DummyPlugin

from conftest import setup_asyncio as setup_function
from conftest import teardown_asyncio as teardown_function


def test_plugin_load():
    config = configparser.ConfigParser()
    config.add_section('plugin:DummyPlugin')
    plugin_list = plugin.get_plugins(config)
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


def test_plugin_found_subscriptions():
    from geoffrey.subscription import subscription, _Subscription
    sub = subscription()
    class TestPlugin(plugin.GeoffreyPlugin):
        @asyncio.coroutine
        def task1(self, mydata: sub) -> plugin.Task:
            yield from asyncio.sleep(1)

    p = TestPlugin(config=None)

    assert len(p.subscriptions) == 1
    assert isinstance(p.subscriptions[0], _Subscription)


def test_plugin_start_tasks_on_start(hub, loop, event):
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
        while True:
            yield from asyncio.sleep(1)

    p = TestPlugin(config=None)

    assert p.data is None
    assert hub.events.qsize() == 0

    hub.add_subscriptions(p.subscriptions)
    loop.run_until_complete(asyncio.wait(p.tasks + [hub.run(), queue_event()],
                                         return_when=asyncio.FIRST_COMPLETED))
    assert p.data == event


def test_plugin_subscription(storeallplugin, hub, event, loop):

   sa_plugin = storeallplugin(config=None)
   hub.add_subscriptions(sa_plugin.subscriptions)

   loop.run_until_complete(hub.put(event))
   assert hub.events.qsize() == 1

   loop.run_until_complete(
       asyncio.wait(sa_plugin.tasks + [hub.run(), asyncio.sleep(1)],
                    return_when=asyncio.FIRST_COMPLETED))

   assert event in sa_plugin.events_received


def test_plugin_new_state(storeallplugin):
    import geoffrey
    from geoffrey.state import StateKey

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)
        server.create_project('newproject')

        project = server.projects['newproject']
        plugin = storeallplugin(config=None, project=project)

        state = plugin.new_state('mykey', value='myvalue')

        statekey = StateKey('newproject', 'StoreAllPlugin', 'mykey')

        assert state.key == statekey
        assert state.value == {'value': 'myvalue'}


def test_plugin_new_event(storeallplugin):
    import geoffrey
    from geoffrey.event import EventType
    from geoffrey.state import StateKey

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)
        server.create_project('newproject')

        project = server.projects['newproject']
        plugin = storeallplugin(config=None, project=project)

        event = plugin.new_event('mykey', value='myvalue')

        statekey = StateKey('newproject', 'StoreAllPlugin', 'mykey')

        assert event.type == EventType.unknown
        assert event.key == statekey
        assert event.value == {'value': 'myvalue'}


def test_plugins_same_hub(storeallplugin, testplugin):
    p1 = storeallplugin(config=None)
    p2 = testplugin(config=None)

    assert p1.hub is p2.hub
