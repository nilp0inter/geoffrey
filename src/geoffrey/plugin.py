import asyncio
import inspect

from geoffrey.deps.straight.plugin import load
from geoffrey.deps.straight.plugin.manager import PluginManager
from geoffrey.subscription import Subscription


class Task:
    """Geoffrey plugin task marker."""
    pass


class GeoffreyPlugin:
    """
    Base plugin.

    """

    def __init__(self, config, hub):
        self.config = config
        self.hub = hub
        self.subscriptions = []
        for task in self.get_tasks():
            kwargs = {}
            for name, subscription in self.get_subscriptions(task):
                self.subscriptions.append(subscription)
                kwargs[name] = subscription
            asyncio.Task(task(self, **kwargs))


    @property
    def name(self):
        return self.__class__.__name__

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
                if isinstance(value, Subscription):
                    yield key, value
        return list(_get_subscriptions())

def get_plugins(config, *args, **kwargs):
    loader = load('geoffrey.plugins',
                  subclasses=GeoffreyPlugin)

    all_plugins = loader.produce(
        config, *args, **kwargs)

    return PluginManager([plugin
                          for plugin in all_plugins
                          if plugin.is_enabled()])
