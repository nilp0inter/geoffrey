import asyncio
import inspect
import logging
import os

from bottle import Bottle

from geoffrey.deps.straight.plugin import load
from geoffrey.deps.straight.plugin.manager import PluginManager
from geoffrey.hub import get_hub
from geoffrey.subscription import _Subscription
from geoffrey.data import State, Event
from geoffrey.utils import slugify, GeoffreyLoggingHandler

logger = logging.getLogger(__name__)
logger.addHandler(GeoffreyLoggingHandler())


class DefaultContextLogger:
    """
    Add geoffrey specific data to logger.

    """
    def __init__(self, logger, project, plugin):
        self.logger = logger
        self.project = project
        self.plugin = plugin

    def _log(self, level, *args, **kwargs):
        extra = kwargs.get('extra', dict())
        extra.setdefault('project', getattr(self.project, 'name', None))
        extra.setdefault('plugin', self.plugin)

        kwargs['extra'] = extra

        getattr(self.logger, level)(*args, **kwargs)

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return self._log(name, *args, **kwargs)
        return wrapper


class Task:
    """Geoffrey plugin task marker."""
    pass


class GeoffreyPlugin:
    """
    Base Geoffrey plugin.

    Uses introspection as a tool to define the desired behavior.

    The methods annotated with result geoffrey.plugin.Task will be
    runned as tasks when the plugin is loaded.

    The methods decored with @geoffrey.subscription can be used as an
    annotation of the Task's parameters as an incomming queue.

    Example:

    .. code-block:: python

        @asyncio.coroutine
        def example(self, events: in_data) -> plugin.Task:
            event = yield from in_data.get()

            # ... some stuff generating states or events ...

            yield from self.hub.put(mystate)  # Put this on the hub

    """
    def __init__(self, config, project=None):
        self.config = config
        self.hub = get_hub()
        self.subscriptions = []
        self.tasks = []
        self._running_tasks = []
        self.project = project
        self.app = Bottle()
        for task in self.get_tasks():
            kwargs = {}
            for name, subscription in self.get_subscriptions(task):
                if isinstance(subscription, str):
                    sub = getattr(self, subscription)()
                else:
                    sub = subscription()  # Instantiate this subscription class
                self.subscriptions.append(sub)
                kwargs[name] = sub
            signature = inspect.signature(task)
            arguments = signature.bind(self, **kwargs)
            self.tasks.append(task(*arguments.args, **arguments.kwargs))

        self.log = DefaultContextLogger(logger, project, self.name)

    def configure_app(self):
        """Override this method to add custom API endpoints."""
        self.app.route('/', callback=self.get_api)

    def get_api(self):
        """Get web API definitions."""
        from geoffrey.utils import get_api
        return get_api(self.app.routes, prefix="/")

    def start(self):
        """
        Start the tasks of this plugin and add its subscriptions to
        the hub.

        """
        self.configure_app()
        for task in self.tasks:  # pragma: no cover
            self._running_tasks.append(asyncio.Task(task))
        self.hub.add_subscriptions(self.subscriptions)
        self.log.info("Started plugin `%s` (%d task(s))",
                      self.name, len(self._running_tasks))

    @property
    def name(self):
        return slugify(self.__class__.__name__)

    def __repr__(self):
        return self.name

    @property
    def _section_name(self):
        """The section name of this plugin in the config file."""
        return 'plugin:' + self.name

    def is_enabled(self):
        section_name = self._section_name
        return section_name in self.config.sections()

    @classmethod
    def get_tasks(cls):
        """
        Return the members of this instance annotated with return Task.

        """
        def _get_tasks():
            members = inspect.getmembers(cls, predicate=inspect.isfunction)
            for _, member in members:
                annotations = getattr(member, '__annotations__', {})
                if annotations.get('return', None) == Task:
                    yield member
        return list(_get_tasks())

    @staticmethod
    def get_subscriptions(task):
        """
        The subscriptions defined as annotations in the tasks methods.

        """
        annotations = getattr(task, '__annotations__', {})
        def _get_subscriptions():
            for key, value in annotations.items():
                if isinstance(value, str):
                    yield key, value
                else:
                    inner_annotation = getattr(value, '__annotations__', {})
                    wrapper_return = inner_annotation.get('return', None)
                    if wrapper_return == _Subscription:
                        yield key, value
        return list(_get_subscriptions())

    @property
    def _project_name(self):
        if self.project is not None:
            return self.project.name

    def new_state(self, key, content_type="data", **kwargs):
        """
        Handy method that for creates a new state prefilled with the
        information of this plugin.

        """

        return State(project=self._project_name, plugin=self.name, key=key,
                     content_type=content_type, **kwargs)

    def new_event(self, key, **kwargs):
        """
        Handy method that for creates a new event prefilled with the
        information of this plugin.

        """
        return Event(project=self._project_name,
                     plugin=self.name, key=key, **kwargs)

    @property
    def static(self):
        """
        Root directory of static files.

        Where the client sources and the assets directory lives.

        """
        classfile = inspect.getfile(self.__class__)
        root = os.path.join(os.path.dirname(classfile), self.name)

        if not os.path.isdir(root):
            return None

        return os.path.realpath(root)

    @property
    def assets(self):
        """
        Root directory of asset files.

        """
        static = self.static
        if static is None:
            return None

        assets = os.path.join(static, 'assets')
        if not os.path.isdir(assets):
            return None

        return assets

    def client_plugin_source(self, language):
        """
        Return the filename of the source code for the client side of this
        plugin in the given language.

        """

        static = self.static
        if static is None:
            return None

        filename = os.path.join(static, "main." + language)
        realfilename = os.path.realpath(filename)

        if not realfilename.startswith(self.static + '/'):  # pragma: no cover
            raise ValueError("Invalid language `%s`" % language)

        if not os.path.isfile(realfilename):
            return None

        return realfilename


def get_plugins(config, *args, **kwargs):
    """
    Returns PluginManager with all available plugins for this config.

    """
    loader = load('geoffreyplugins',
                  subclasses=GeoffreyPlugin)

    all_plugins = loader.produce(
        config, *args, **kwargs)

    return PluginManager([plugin
                          for plugin in all_plugins
                          if plugin.is_enabled()])

def get_all_plugins(config, *args, **kwargs):
    """
    Returns PluginManager with all available plugins in the system.

    """
    loader = load('geoffreyplugins',
                  subclasses=GeoffreyPlugin)

    all_plugins = loader.produce(
        config, *args, **kwargs)

    return PluginManager([plugin for plugin in all_plugins])
