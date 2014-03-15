"""
Servidor de geoffrey.

"""
# pylint: disable=I0011, E1101
from asyncio import subprocess

import webbrowser
import asyncio
import logging
import os
import sys
import websockets
from fnmatch import fnmatch

from pyinotify import WatchManager, ThreadedNotifier, EventsCodes

logging.basicConfig(level=logging.INFO)


@asyncio.coroutine
def websocket_server(websocket, uri):
    """
    Sirve el resultado de la ejecución de pylint por el websocket.

    """
    logging.info("New connection from %s. %s", uri, websocket)

    queue = asyncio.Queue()
    asyncio.async(watch_files(queue, sys.argv[1]))
    while True:
        event = yield from queue.get()
        filename = os.path.join(event.path, event.name)
        if fnmatch(filename, '*.py'):
            print("< {}".format(filename))
            #_, stdout, _ = yield from getstatusoutput(
            #    '/home/nil/Envs/geoffrey/bin/pylint',
            #    '--rcfile=/home/nil/Projects/geoffrey/.pylintrc',
            #    filename)
            _, stdout, _ = yield from getstatusoutput(
                '/home/nil/Envs/geoffrey/bin/radon',
                'cc', '-a',
                filename)
            print("> {}".format(stdout))
            yield from websocket.send(stdout.decode('utf-8'))


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
def watch_files(queue, path):
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

    watcher.add_watch(path, mask, rec=True)
    while True:
        notifier.process_events()
        event_present = yield from asyncio.get_event_loop().run_in_executor(
            None, notifier.check_events)
        if event_present:
            notifier.read_events()


if __name__ == '__main__':
    webbrowser.open('file:///home/nil/Projects/geoffrey/websocket.html')
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(websocket_server, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()
