import asyncio
import configparser

import pytest

from geoffrey import plugin
from geoffrey.plugins.dummy import DummyPlugin


def test_plugin_load():
    config = configparser.ConfigParser()
    config.add_section('plugin:DummyPlugin')
    plugin_list = plugin.get_plugins(config)
    assert any([isinstance(p, DummyPlugin) for p in plugin_list])

@pytest.mark.wip
def test_plugin_subscription(storeallplugin, hub, event, loop):

   hub.add_subscriptions(storeallplugin.subscriptions)

   loop.run_until_complete(hub.put(event))
   assert hub.events.qsize() == 1

   loop.run_until_complete(
       asyncio.wait([hub.run(), asyncio.sleep(1)],
                    return_when=asyncio.FIRST_COMPLETED))

   assert event in storeallplugin.events_received
