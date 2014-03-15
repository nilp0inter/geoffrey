"""
Servidor de geoffrey.

"""
# pylint: disable=I0011, E1101
import argparse
from asyncio import subprocess

import webbrowser
import asyncio
import logging
import os
import sys
import websockets
from fnmatch import fnmatch

from pyinotify import WatchManager, ThreadedNotifier, EventsCodes
from rainfall.web import Application, HTTPHandler

from geoffrey import default
from geoffrey.config import Config
from geoffrey.plugin import EventManager, get_plugins

logging.basicConfig(level=logging.DEBUG)

event_queue = asyncio.Queue()
output_queue = asyncio.Queue()


@asyncio.coroutine
def websocket_server(websocket, uri):
    """
    Sirve el resultado de la ejecución de pylint por el websocket.

    """
    logging.info("New connection from %s. %s", uri, websocket)

    while True:
        output = yield from output_queue.get()
        try:
            yield from websocket.send(output.decode('utf-8'))
        except websockets.exceptions.InvalidState as err:
            logging.error('Invalid socket state %s', err)
            yield from output_queue.put(output)
            return False


@asyncio.coroutine
def watch_files(paths, mask):
    """
    Vigila los ficheros de path y encola en queue los eventos producidos.

    """
    watcher = WatchManager()
    mask = (EventsCodes.ALL_FLAGS.get('IN_MODIFY', 0))

    @asyncio.coroutine
    def send_event(event):
        """Encola un evento en la cola."""
        yield from event_queue.put(event)

    notifier = ThreadedNotifier(
        watcher,
        lambda e: asyncio.get_event_loop().call_soon_threadsafe(
            asyncio.async, send_event(e)))

    for path in paths:
        watcher.add_watch(path, mask, rec=True)

    while True:
        notifier.process_events()
        event_present = yield from asyncio.get_event_loop().run_in_executor(
            None, notifier.check_events)
        if event_present:
            notifier.read_events()


def get_app(config, args):
    main = config['geoffrey']
    host = main.get('host', default.HOST)
    websocket_port = main.get('websocket_port', default.WEBSOCKET_PORT)
    webserver_port = main.get('webserver_port', default.WEBSERVER_PORT)

    class DashboardHandler(HTTPHandler):
        def handle(self, request):
            return self.render('index.html',
                               host=host,
                               port=websocket_port,
                               path=args.path)

    settings = {
        'template_path': os.path.join(os.path.dirname(__file__), "web"),
        'host': host,
        'port': str(webserver_port),
    }

    app = Application(
        {
            r'^/$': DashboardHandler(),
        },
        settings=settings
    )
    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=default.GEOFFREY_RC_FILE)
    parser.add_argument('path', nargs='+')
    args = parser.parse_args()
    print(args.config)
    config = Config(args.config, create=True)

    main = config['geoffrey']
    host = main.get('host', default.HOST)
    websocket_port = main.get('websocket_port', default.WEBSOCKET_PORT)
    webserver_port = main.get('webserver_port', default.WEBSERVER_PORT)

    loop = asyncio.get_event_loop()

    em = EventManager()
    plugins = get_plugins(config, output_queue)
    for subscriptions in plugins.call('get_subscriptions'):
        em.add_subscriptions(subscriptions)

    mask = em.get_mask()

    asyncio.Task(websockets.serve(websocket_server, host, websocket_port))

    asyncio.Task(watch_files(args.path, mask=mask))
    asyncio.Task(em.consume_events(event_queue, output_queue))

    #webbrowser.open('http://{host}:{port}'.format(host=host,
    #                                              port=webserver_port))
    get_app(config, args).run()
