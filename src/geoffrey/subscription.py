import asyncio

ANYTHING = lambda x: True
NOTHING = lambda x: False


class Subscription:
    def __init__(self, loop):
        self.allow_funcs = []
        self.callbacks = []
        self.queue = asyncio.Queue(loop=loop)
        self.active = True
        self._run_once = False
        self.loop = loop

    def add_filter(self, filter_func):
        self.allow_funcs.append(filter_func)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    @asyncio.coroutine
    def put(self, data):
        if any(f(data) for f in self.allow_funcs):
            yield from self.queue.put(data)

    @asyncio.coroutine
    def run(self):
        while self.active:
            data = yield from self.queue.get()
            for callback in self.callbacks:
                future = yield from self.loop.run_in_executor(
                    None, callback, data)

            if self._run_once:
                break
