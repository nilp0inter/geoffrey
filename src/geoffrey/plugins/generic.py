import difflib
import magic
from fnmatch import fnmatch
from geoffrey.data import HTML
from geoffrey.plugin import GeoffreyPlugin


class FileDiff(GeoffreyPlugin):

    diff = difflib.HtmlDiff()
    files = {}

    def run(self, filename):
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_type = m.id_filename(filename)
            if not fnmatch(file_type, '*text*'):
                return False

        with open(filename, 'r') as f:
            content = f.readlines()

        if filename in self.files:
            if self.files[filename] != content:
                output = HTML(self.diff.make_table(self.files[filename],
                                                   content))
                yield from self.output_queue.put(output)

        self.files[filename] = content
