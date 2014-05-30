import os
import asyncio
import configparser
import logging
import json
import watchdog
import pytest
import geoffrey
from conftest import setup_asyncio as setup_function
from conftest import teardown_asyncio as teardown_function

# logging.basicConfig(level = logging.DEBUG)

def test_plugin_exist():
    from geoffrey.plugins.filesystem import FileSystem
    assert FileSystem


def test_monitor_directory(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    import logging
    logging.basicConfig(level=logging.DEBUG)

    sa_plugin = storeallplugin(config=None, stop_after=1)

    with TemporaryDirectory() as path:
        config = configparser.ConfigParser()
        config.add_section('plugin:FileSystem')
        config.set('plugin:FileSystem', 'paths', path)

        @asyncio.coroutine
        def create_file():
            yield from asyncio.sleep(1)
            with open(os.path.join(path, 'test.txt'), 'w') as f:
                pass
            while True:
                yield from asyncio.sleep(1)

        fs_plugin = FileSystem(config=config)

        hub.add_subscriptions(sa_plugin.subscriptions)

        tasks = fs_plugin.tasks + sa_plugin.tasks + [hub.run(), create_file()]
        loop.run_until_complete(
            asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))

    assert len(sa_plugin.events_received) == 1


def test_monitor_multiple_path(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    sa_plugin = storeallplugin(config=None, stop_after=2)

    with TemporaryDirectory() as path1:
        with TemporaryDirectory() as path2:
            config = configparser.ConfigParser()
            config.add_section('plugin:FileSystem')
            config.set('plugin:FileSystem', 'paths', ','.join((path1, path2)))

            @asyncio.coroutine
            def create_files():
                yield from asyncio.sleep(1)
                with open(os.path.join(path1, 'test1.txt'), 'w') as f:
                    pass
                with open(os.path.join(path2, 'test2.txt'), 'w') as f:
                    pass
                while True:
                    yield from asyncio.sleep(1)

            fs_plugin = FileSystem(config=config)

            hub.add_subscriptions(sa_plugin.subscriptions)

            loop.run_until_complete(
                asyncio.wait(fs_plugin.tasks + sa_plugin.tasks + \
                             [create_files(), hub.run()],
                             return_when=asyncio.FIRST_COMPLETED))

    assert len(sa_plugin.events_received) == 2


def test_event_data(loop, storeallplugin, hub):
    from geoffrey.plugins.filesystem import FileSystem
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)
        server.create_project('newproject')
        project = server.projects['newproject']

        sa_plugin = storeallplugin(config=None, stop_after=1, project=project)

        newfile = os.path.join(configdir, 'test.txt')

        @asyncio.coroutine
        def create_file():
            yield from asyncio.sleep(1)
            with open(newfile, 'w') as f:
                pass

            while True:
                yield from asyncio.sleep(1)

        fs_config = configparser.ConfigParser()
        fs_config.add_section('plugin:FileSystem')
        fs_config.set('plugin:FileSystem', 'paths', configdir)

        fs_plugin = FileSystem(config=fs_config, project=project)
        hub.add_subscriptions(sa_plugin.subscriptions)

        loop.run_until_complete(
            asyncio.wait(fs_plugin.tasks + sa_plugin.tasks + \
                         [create_file(), hub.run()],
                         return_when=asyncio.FIRST_COMPLETED))

        event = sa_plugin.events_received[0]
        data = json.loads(event.dumps())

        assert data['project'] == "newproject"
        assert data['plugin'] == "FileSystem"
        assert data['key'] == newfile
        assert data['value'] == {'type': 'created'}
