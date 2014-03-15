from geoffrey.plugin import GeoffreyPlugin, getstatusoutput

class PyLint(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/pylint',
                                                  filename)
        yield from self.output_queue.put(stdout)

class Flake8(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/flake8',
                                                  filename)
        yield from self.output_queue.put(stdout)


class RadonRAW(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'raw',
                                                  filename)
        yield from self.output_queue.put(stdout)


class RadonCC(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'cc',
                                                  filename)
        yield from self.output_queue.put(stdout)


class RadonMI(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'mi',
                                                  filename)
        yield from self.output_queue.put(stdout)
