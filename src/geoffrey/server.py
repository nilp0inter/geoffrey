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

from config import Config

logging.basicConfig(level=logging.INFO)

queue = asyncio.Queue()
HOST = '127.0.0.1'
WEBSERVER_PORT = 8888
WEBSOCKET_PORT = 8765


@asyncio.coroutine
def websocket_server(websocket, uri):
    """
    Sirve el resultado de la ejecución de pylint por el websocket.

    """
    logging.info("New connection from %s. %s", uri, websocket)

    while True:
        event = yield from queue.get()
        filename = os.path.join(event.path, event.name)
        if fnmatch(filename, '*.py'):
            print("< {}".format(filename))
            _, stdout, _ = yield from getstatusoutput(
                '/home/nil/Envs/geoffrey/bin/pylint',
                '--rcfile=/home/nil/Projects/geoffrey/.pylintrc',
                filename)
            #_, stdout, _ = yield from getstatusoutput(
            #    '/home/nil/Envs/geoffrey/bin/radon',
            #    'cc', '-a',
            #    filename)
            print("> {}".format(stdout))
            try:
                yield from websocket.send(stdout.decode('utf-8'))
            except websockets.exceptions.InvalidState as err:
                logging.error('Invalid socket state %s', err)
                return False


@asyncio.coroutine
def getstatusoutput(*args):
    """
    Devuelve el resultado de la ejecución de un comando.

    """
    proc = yield from asyncio.create_subprocess_exec(*args,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.STDOUT)
    try:
        stdout, stderr = yield from proc.communicate()
    except:
        proc.kill()
        yield from proc.wait()
        raise
    exitcode = yield from proc.wait()
    return (exitcode, stdout, stderr)


@asyncio.coroutine
def watch_files(paths):
    """
    Vigila los ficheros de path y encola en queue los eventos producidos.

    """
    watcher = WatchManager()
    mask = (EventsCodes.ALL_FLAGS.get('IN_MODIFY', 0))

    @asyncio.coroutine
    def send_event(event):
        """Encola un evento en la cola."""
        yield from queue.put(event)

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
    host = main.get('host', HOST)
    websocket_port = main.get('websocket_port', WEBSOCKET_PORT)
    webserver_port = main.get('webserver_port', WEBSERVER_PORT)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configfile = os.path.join(os.path.expanduser('~'), '.goeffreyrc')
    parser.add_argument('-c', '--config', default=configfile)
    parser.add_argument('path', nargs='+')
    args = parser.parse_args()
    print(args.config)
    config = Config(args.config, create=True)

    main = config['geoffrey']
    host = main.get('host', HOST)
    websocket_port = main.get('websocket_port', WEBSOCKET_PORT)
    webserver_port = main.get('webserver_port', WEBSERVER_PORT)

    loop = asyncio.get_event_loop()

    asyncio.Task(websockets.serve(websocket_server, host, websocket_port))

    asyncio.Task(watch_files(args.path))

    webbrowser.open('http://{host}:{port}'.format(host=host,
                                                  port=webserver_port))
    get_app(config, args).run()
