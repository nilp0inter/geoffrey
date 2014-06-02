import asyncio
import logging
import os

from .server import Server

FORMAT = '%(asctime)-15s [%(levelname)-8s] %(name)s: %(message)s'

logger = logging.getLogger(__name__)

@asyncio.coroutine
def print_tasks():
    while True:
        yield from asyncio.sleep(3)
        logger.debug("Tasks: %s", asyncio.Task.all_tasks())

def main():
    """Function used by the main console entry_point."""

    if os.environ.get('GEOFFREYDEBUG', '0') == '1':
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel, format=FORMAT)

    if os.environ.get('PYTHONASYNCIODEBUG', '0') == '0':
        asyncio_logger = logging.getLogger('asyncio')
        asyncio_logger.setLevel(logging.WARNING)
    else:
        _print_tasks = asyncio.Task(print_tasks())

    server = Server()
    server.run()
