import os
import asyncio
import configparser
import logging
import json
import watchdog
import pytest
import geoffrey

# logging.basicConfig(level = logging.DEBUG)


def test_plugin_exist():
    from geoffrey.plugins.filesystem import FileSystem
    assert FileSystem


def test_monitor_directory(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    storeallplugin = storeallplugin(config=None)
    storeallplugin.start()

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
        plugin.start()
        hub.add_subscriptions(storeallplugin.subscriptions)

        loop.run_until_complete(
            asyncio.wait([stop_after_3(plugin), hub.run()],
                         return_when=asyncio.FIRST_COMPLETED))
    assert len(storeallplugin.events_received) == 1


def test_monitor_multiple_path(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    storeallplugin = storeallplugin(config=None)
    storeallplugin.start()

    with TemporaryDirectory() as path1:
        with TemporaryDirectory() as path2:
            config = configparser.ConfigParser()
            config.add_section('plugin:FileSystem')
            config.set('plugin:FileSystem', 'paths', ','.join((path1, path2)))

            @asyncio.coroutine
            def stop_after_3(plugin):
                yield from asyncio.sleep(1)
                with open(os.path.join(path1, 'test1.txt'), 'w') as f:
                    pass
                with open(os.path.join(path2, 'test2.txt'), 'w') as f:
                    pass
                yield from asyncio.sleep(1)
                plugin.active = False
                yield from asyncio.sleep(1)

            plugin = FileSystem(config=config)
            plugin.start()

            hub.add_subscriptions(storeallplugin.subscriptions)

            loop.run_until_complete(
                asyncio.wait([stop_after_3(plugin), hub.run()],
                             return_when=asyncio.FIRST_COMPLETED))

    assert len(storeallplugin.events_received) == 2


def test_monitor_directory(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)
        server.create_project('newproject')
        project = server.projects['newproject']

        sa_plugin = storeallplugin(config=None, project=project)
        sa_plugin.start()

        newfile = os.path.join(configdir, 'test.txt')

        @asyncio.coroutine
        def stop_after_3(plugin):
            yield from asyncio.sleep(1)
            with open(newfile, 'w') as f:
                pass
            yield from asyncio.sleep(1)
            plugin.active = False
            yield from asyncio.sleep(1)

        fs_config = configparser.ConfigParser()
        fs_config.add_section('plugin:FileSystem')
        fs_config.set('plugin:FileSystem', 'paths', configdir)

        fs_plugin = FileSystem(config=fs_config, project=project)
        fs_plugin.start()
        hub.add_subscriptions(sa_plugin.subscriptions)

        loop.run_until_complete(
            asyncio.wait([stop_after_3(sa_plugin), hub.run()],
                         return_when=asyncio.FIRST_COMPLETED))

        event = storeallplugin.events_received[0]
        data = json.loads(event.dumps())

        assert data['project'] == "newproject"
        assert data['plugin'] == "FileSystem"
        assert data['key'] == newfile
        assert data['value'] == {'type': 'created'}
