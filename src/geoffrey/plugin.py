import asyncio
import logging
import inspect

from geoffrey.deps.straight.plugin import load
from geoffrey.deps.straight.plugin.manager import PluginManager
from geoffrey.hub import get_hub
from geoffrey.subscription import _Subscription
from geoffrey.state import State
from geoffrey.event import Event

logger = logging.getLogger(__name__)

class Task:
    """Geoffrey plugin task marker."""
    pass


class GeoffreyPlugin:
    """
    Base plugin.

    """
    def __init__(self, config, project=None):
        self.config = config
        self.hub = get_hub()
        self.subscriptions = []
        self.tasks = []
        self._running_tasks = []
        self.project = project
        for task in self.get_tasks():
            kwargs = {}
            for name, subscription in self.get_subscriptions(task):
                sub = subscription()  # Instantiate this subscription class
                self.subscriptions.append(sub)
                kwargs[name] = sub
            self.tasks.append(task(self, **kwargs))

    def start(self):
        for task in self.tasks:  # pragma: no cover
            self._running_tasks.append(asyncio.Task(task))
        self.hub.add_subscriptions(self.subscriptions)
        logger.info("Started plugin `%s` (%d task(s))",
                    self.name, len(self._running_tasks))

    @property
    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.name

    @property
    def _section_name(self):
        return 'plugin:' + self.name

    def is_enabled(self):
        section_name = self._section_name
        return section_name in self.config.sections()

    @classmethod
    def get_tasks(cls):
        """
        Return the members of this class annotated with return Task.
        """
        def _get_tasks():
            members = inspect.getmembers(cls,predicate=inspect.isfunction)
            for name, member in members:
                annotations = getattr(member, '__annotations__', {})
                if annotations.get('return', None) == Task:
                    yield member
        return list(_get_tasks())

    @staticmethod
    def get_subscriptions(task):
        annotations = getattr(task, '__annotations__', {})
        def _get_subscriptions():
            for key, value in annotations.items():
                inner_annotattion = getattr(value, '__annotations__', {})
                wrapper_return = inner_annotattion.get('return', None)
                if wrapper_return == _Subscription:
                    yield key, value
        return list(_get_subscriptions())

    @property
    def _project_name(self):
        if self.project is not None:
            return self.project.name

    def new_state(self, key, **kwargs):
        return State(project=self._project_name,
                     plugin=self.name, key=key, **kwargs)

    def new_event(self, key, **kwargs):
        state = self.new_state(key, **kwargs)
        return Event(key=state.key, value=state.value)


def get_plugins(config, *args, **kwargs):
    loader = load('geoffrey.plugins',
                  subclasses=GeoffreyPlugin)

    all_plugins = loader.produce(
        config, *args, **kwargs)

    return PluginManager([plugin
                          for plugin in all_plugins
                          if plugin.is_enabled()])
