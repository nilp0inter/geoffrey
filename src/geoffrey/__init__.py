from .server import Server


def main():
    """Function used by the main console entry_point."""
    server = Server()
    server.run()
