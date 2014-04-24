import asyncio
import logging

ANYTHING = lambda x: True

logger = logging.getLogger(__name__)


class _Subscription(asyncio.Queue):
    """
    Special type of `Queue` that only accepts data if match the filter
    function.

    """
    def __init__(self, *args, filter_func=None, **kwargs):
        if filter_func is None:
            filter_func = ANYTHING
        self.filter_func = filter_func
        super().__init__(*args, **kwargs)

    @asyncio.coroutine
    def put(self, item):
        logging.debug("Subscription %r received item %r", self, item)
        if self.filter_func(item):
            logging.debug("Subscription %r accepted item %r", self, item)
            yield from super().put(item)

def subscription(*args, filter_func=ANYTHING, **kwargs):
    """
    Wrapper for _Subscription.
    """
    def wrapper() -> _Subscription:
        return _Subscription(*args, filter_func=filter_func, **kwargs)
    return wrapper
