import asyncio

ANYTHING = lambda x: True


class Subscription:
    def __init__(self, loop):
        self.allow_funcs = []
        self.queue = asyncio.Queue(loop=loop)

    def add_filter(self, filter_func):
        self.allow_funcs.append(filter_func)

    @asyncio.coroutine
    def put(self, data):
        if any(f(data) for f in self.allow_funcs):
            yield from self.queue.put(data)
