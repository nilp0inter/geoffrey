import logging
import json
from geoffrey.plugin import GeoffreyPlugin
from geoffrey.utils import GeoffreyLoggingHandler

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
