import asyncio

ANYTHING = lambda x: True


class Subscription(asyncio.Queue):
    """
    Special type of `Queue` that only accepts data if match the filter
    function.

    """
    def __init__(self, *args, filter_func=lambda x: True, **kwargs):
        self.filter_func = filter_func
        super().__init__(*args, **kwargs)

    @asyncio.coroutine
    def put(self, item):
        if self.filter_func(item):
            yield from super().put(item)
