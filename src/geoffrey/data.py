from collections import namedtuple

Location = namedtuple('Location', ['namespace', 'object', 'plugin'])


class Data:
    @property
    def location(self):
        return Location(namespace=self.namespace,
                        object=self.object,
                        plugin=self.plugin)


class Event(Data):
    pass


class Status(Data):
    pass
