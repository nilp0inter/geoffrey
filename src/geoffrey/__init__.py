import asyncio
import configparser
import os
import signal

loop = asyncio.get_event_loop()
DEFAULT_CONFIG_FILENAME = os.path.join(os.path.expanduser('~'),
                                       '.geoffrey',
                                       'geoffrey.conf')


def handle_ctrl_c():
    # TODO: Use logging
    print("Exiting...")
    loop.stop()


def main():
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILENAME)
    loop.add_signal_handler(signal.SIGINT, handle_ctrl_c)
    loop.run_forever()
