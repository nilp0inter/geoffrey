import asyncio
import logging
import os

from geoffrey.server import Server
from geoffrey.utils import GeoffreyLoggingHandler

FORMAT = '%(asctime)-15s [%(levelname)-8s] %(name)s: %(message)s'

logger = logging.getLogger(__name__)

@asyncio.coroutine
def print_tasks():
    while True:
        yield from asyncio.sleep(3)
        logger.debug("Tasks: %s", asyncio.Task.all_tasks())
        for task in asyncio.Task.all_tasks():
            if task.done():
                try:
                    logger.info("Task %s done: %s", task, task.result())
                except:
                    logger.exception("Task %s failed: %s", task)

def main():
    """Function used by the main console entry_point."""

    if os.environ.get('GEOFFREYDEBUG', '0') == '1':
        loglevel = logging.DEBUG
        _print_tasks = asyncio.Task(print_tasks())
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel, format=FORMAT)

    if 'PYTHONASYNCIODEBUG' in os.environ:
        logger.critical((
            "Please unset the environment variable PYTHONASYNCIODEBUG."
            "http://bugs.python.org/issue21209"))
        return 1

    hub_handler = GeoffreyLoggingHandler()
    hub_handler.setLevel(logging.DEBUG)
    logger.addHandler(hub_handler)

    server = Server()
    server.run()

if __name__ == '__main__':
    main()
