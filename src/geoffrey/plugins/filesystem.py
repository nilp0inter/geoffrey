import asyncio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from geoffrey.plugin import GeoffreyPlugin
from geoffrey.event import Event, EventType

logger = logging.getLogger(__name__)


class GeoffreyFSHandler(FileSystemEventHandler):
    def __init__(self, loop, hubs):
        self.loop = loop
        self.hubs = hubs

    def on_any_event(self, event):
        logger.debug("Received FS event %r", event)
        gev = Event(type=event.event_type,
                    key=event.src_path)
        for hub in self.hubs:
            self.loop.call_soon_threadsafe(asyncio.async, hub.put(gev))


class FileSystem(GeoffreyPlugin):
    """
    Filesystem monitor.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True
        self.hubs = []

    def add_hub(self, hub):
        self.hubs.append(hub)

    @asyncio.coroutine
    def run(self):
        event_handler = GeoffreyFSHandler(asyncio.get_event_loop(), self.hubs)
        observer = Observer()
        observer.schedule(
            event_handler,
            self.config.get(self._section_name, 'paths'),
            recursive=True)
        observer.start()
        while self.active:
            yield from asyncio.sleep(1)
        observer.stop()
        observer.join()
