import asyncio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from geoffrey import plugin
from geoffrey.event import Event, EventType

logger = logging.getLogger(__name__)


class GeoffreyFSHandler(FileSystemEventHandler):
    def __init__(self, loop, plugin):
        self.loop = loop
        self.plugin = plugin

    def on_any_event(self, event):
        logger.debug("Received FS event %r", event)
        event = self.plugin.new_event(
            key=event.src_path.decode('utf-8'), type=event.event_type)
        self.loop.call_soon_threadsafe(
            asyncio.async, self.plugin.hub.put(event))


class FileSystem(plugin.GeoffreyPlugin):
    """
    Filesystem monitor.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True

    @asyncio.coroutine
    def run(self) -> plugin.Task:
        event_handler = GeoffreyFSHandler(asyncio.get_event_loop(),
                                          plugin=self)
        observer = Observer()
        paths = self.config.get(self._section_name, 'paths').split(',')
        for path in paths:
            observer.schedule(event_handler, path, recursive=True)
        observer.start()
        while self.active:
            yield from asyncio.sleep(1)
        observer.stop()
        observer.join()
