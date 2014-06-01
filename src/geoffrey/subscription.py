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
        if self.filter_func(item):
            # logger.debug("Subscription %s allow event %s", id(self), item)
            yield from super().put(item)
        else:
            # logger.debug("Subscription %s reject event %s", id(self), item)
            pass

    def put_nowait(self, item):
        if self.filter_func(item):
            # logger.debug("Subscription %s allow event %s", id(self), item)
            return super().put_nowait(item)
        else:
            # logger.debug("Subscription %s reject event %s", id(self), item)
            pass


class Consumer(_Subscription):

    """Special type of subscription with mutable criteria."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, filter_func=self.match, **kwargs)
        self.criteria = []

    def match(self, event):
        """Return `True` if any criteria match."""
        return any(self._match(c, event) for c in self.criteria)

    def _match(self, criteria, event):
        """Return `True` if this criteria match this event."""
        def match_or_fail(name, data):
            criteria_item = criteria.get(name, None)
            if criteria_item is not None:
                if criteria_item != data:
                    return False
            return True

        return all((match_or_fail('type', event.type.name),
                    match_or_fail('project', event.key.project),
                    match_or_fail('plugin', event.key.plugin),
                    match_or_fail('key', event.key.key)))


def subscription(*args, filter_func=ANYTHING, **kwargs):
    """
    Wrapper for _Subscription.
    """
    def wrapper() -> _Subscription:
        return _Subscription(*args, filter_func=filter_func, **kwargs)
    return wrapper
