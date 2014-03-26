import asyncio
import signal

loop = asyncio.get_event_loop()


def handle_ctrl_c():
    # TODO: Use logging
    print("Exiting...")
    loop.stop()


def main():
    loop.add_signal_handler(signal.SIGINT, handle_ctrl_c)
    loop.run_forever()
