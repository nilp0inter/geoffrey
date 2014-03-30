import logging

from .server import Server

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'


def main():
    """Function used by the main console entry_point."""
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    server = Server()
    server.run()
