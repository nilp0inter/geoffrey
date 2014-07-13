#pylint: disable=E1101
import argparse
import asyncio
import logging
import os

from geoffrey.server import Server

FORMAT = '%(asctime)-15s [%(levelname)-8s] %(name)s: %(message)s'

logger = logging.getLogger(__name__)

@asyncio.coroutine
def print_tasks():
    """
    Print all asyncio tasks continuosly in debug mode.
    XXX: Figure out why `done` tasks are not deleted.

    """
    while True:
        yield from asyncio.sleep(10)
        for task in asyncio.Task.all_tasks():
            if task.done():
                exception = task.exception()
                if exception is None:
                    logger.info("Task DONE: %s = %s", task, task.result())
                else:
                    logger.error("Task FAILED: %s = %s", task, exception)
            else:
                logger.debug("Tasks RUNNING: %s", task)

def main():
    """Function used by the main console entry_point."""
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    if os.environ.get('GEOFFREYDEBUG', '0') == '1':
        loglevel = logging.DEBUG
        asyncio.Task(print_tasks())
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel, format=FORMAT)

    if 'PYTHONASYNCIODEBUG' in os.environ:
        logger.critical((
            "Please unset the environment variable PYTHONASYNCIODEBUG."
            "http://bugs.python.org/issue21209"))
        return 1

    server = Server()
    server.run()
