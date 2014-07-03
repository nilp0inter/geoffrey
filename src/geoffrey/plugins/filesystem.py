import asyncio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from geoffrey import plugin
from geoffrey.data import Event, EventType

logger = logging.getLogger(__name__)


class GeoffreyFSHandler(FileSystemEventHandler):
    def __init__(self, loop, plugin):
        self.loop = loop
        self.plugin = plugin

    def on_any_event(self, event):
        self.plugin.log.debug("Received FS event %r", event)
        self.loop.call_soon_threadsafe(asyncio.async,
                                       self.plugin.queue_event(event))


class FileSystem(plugin.GeoffreyPlugin):
    """
    Filesystem monitor.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active = True

    @asyncio.coroutine
    def queue_event(self, fsevent):
        if isinstance(fsevent.src_path, bytes):
            key = fsevent.src_path.decode('utf-8')
        else:
            key = fsevent.src_path
        type_ = fsevent.event_type
        event = self.new_event(key=key, fs_event=type_)
        yield from self.hub.put(event)

    def stop(self):
        """Stop the observer thread and exit."""
        self._active = False

    @asyncio.coroutine
    def capture_fs_events(self) -> plugin.Task:
        event_handler = GeoffreyFSHandler(asyncio.get_event_loop(),
                                          plugin=self)
        observer = Observer()
        paths = self.config.get(self._section_name, 'paths').split(',')
        for path in paths:
            observer.schedule(event_handler, path, recursive=True)
        observer.start()
        while self._active:  # pragma: no branch
            yield from asyncio.sleep(1)
        observer.stop()
        observer.join()
