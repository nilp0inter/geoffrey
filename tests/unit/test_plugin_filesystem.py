import os
import asyncio
import configparser
import logging
import watchdog

# logging.basicConfig(level = logging.DEBUG)

def test_plugin_exist():
    from geoffrey.plugins.filesystem import FileSystem
    assert FileSystem

def test_monitor_directory(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as path:
        config = configparser.ConfigParser()
        config.add_section('plugin:FileSystem')
        config.set('plugin:FileSystem', 'paths', path)

        @asyncio.coroutine
        def stop_after_3(plugin):
            yield from asyncio.sleep(1)
            with open(os.path.join(path, 'test.txt'), 'w') as f:
                pass
            yield from asyncio.sleep(1)
            plugin.active = False
            yield from asyncio.sleep(1)

        plugin = FileSystem(config=config)
        plugin.add_hub(hub)
        hub.add_subscriptions(storeallplugin.subscriptions)
        hub._run_once = True

        loop.run_until_complete(asyncio.wait(
            [stop_after_3(plugin), plugin.run(), hub.run()]))
    assert len(storeallplugin.events_received) == 1
