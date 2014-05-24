import logging
import os

from .server import Server

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'

logger = logging.getLogger(__name__)

def main():
    """Function used by the main console entry_point."""

    if os.environ.get('GEOFFREYDEBUG', '0') == '1':
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    server = Server()
    logging.basicConfig(level=loglevel, format=FORMAT)
    server.run()
