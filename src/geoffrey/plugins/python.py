from glob import glob
import os
import tempfile

from geoffrey.data import Text, Image
from geoffrey.plugin import GeoffreyPlugin, getstatusoutput


class PyLint(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/pylint',
                                                  filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))


class Flake8(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/flake8',
                                                  filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))


class RadonRAW(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'raw',
                                                  filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))


class RadonCC(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'cc',
                                                  filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))


class RadonMI(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/radon',
                                                  'mi',
                                                  filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))


class PyReverse(GeoffreyPlugin):
    def run(self, filename):
        runname = os.path.basename(tempfile.mktemp())
        _, _, _ = yield from getstatusoutput('/usr/local/bin/pyreverse',
                                             '-SA', '-o', 'png', '-p', runname,
                                             filename)

        for filename in glob('*{}*.png'.format(runname)):
            with open(filename, 'rb') as f:
                image = Image(f.read())
                yield from self.output_queue.put(image)
            os.unlink(filename)


class CheeseCake(GeoffreyPlugin):
    def run(self, filename):
        _, stdout, _ = yield from getstatusoutput('/usr/local/bin/cheesecake_index',
                                                  '-p', filename)
        yield from self.output_queue.put(Text(stdout.decode('utf-8')))
