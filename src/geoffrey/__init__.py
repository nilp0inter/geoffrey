import asyncio
import configparser
import os
import signal

loop = asyncio.get_event_loop()
DEFAULT_CONFIG_FILENAME = os.path.join(os.path.expanduser('~'),
                                       '.geoffrey',
                                       'geoffrey.conf')


def read_main_config(filename=DEFAULT_CONFIG_FILENAME):
    if not os.path.isfile(filename):
        # Config does not exists. Create the default one.
        with open(filename, 'w') as f:
            f.write('[geoffrey]\n\n')

    config = configparser.ConfigParser()
    config.read(filename)
    return config


def handle_ctrl_c():
    # TODO: Use logging
    print("Exiting...")
    loop.stop()


def main():
    config = read_main_config()
    loop.add_signal_handler(signal.SIGINT, handle_ctrl_c)
    loop.run_forever()
