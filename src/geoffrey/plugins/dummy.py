"""
dummy plugin module

"""
import logging
from geoffrey.plugin import GeoffreyPlugin

logger = logging.getLogger(__name__)


class DummyPlugin(GeoffreyPlugin):
    """
    Dummy plugin for testing.

    """

    pass


class DummyPlugin1(DummyPlugin):
    """
    Dummy plugin for testing.

    """
    pass


class DummyPlugin2(DummyPlugin):
    """
    Dummy plugin for testing.

    """
    pass
