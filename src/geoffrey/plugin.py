import inspect

from geoffrey.data import Data


class Plugin:
    def __init__(self, config, datamanager):
        self.config = config
        self.data = datamanager

    def get_tasks(self):
        for _, method in inspect.getmembers(self,
                                            predicate=inspect.ismethod):
            signature = inspect.signature(method)
            if issubclass(signature.return_annotation, Data):
                yield (method, signature)
