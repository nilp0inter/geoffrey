"""
The filecontent plugin.

"""
import asyncio
import os
import hashlib
from fnmatch import fnmatch

import magic

from geoffrey import plugin
from geoffrey.subscription import subscription


class FileContent(plugin.GeoffreyPlugin):
    """
    The filecontent manages filesystem changes and emit states with
    the file content.

    """
    def _match(self, expressions, data):
        for exp in expressions:
            yield fnmatch(data, exp.strip())

    @subscription
    def modified_files(event):
        """Filed modified by the user."""
        return (event.plugin == "filesystem" and
                event.fs_event == "modified")

    @asyncio.coroutine
    def read_modified_files(self, events: modified_files) -> plugin.Task:
        try:
            exclude_exp = self.config.get(self._section_name,
                                          'exclude').split(',')
        except:
            exclude_exp = ""

        try:
            include_exp = self.config.get(self._section_name,
                                          'include').split(',')
        except:
            include_exp = ""

        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as mime:
            with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as encoding:
                while True:

                    event = yield from events.get()

                    if not (any(self._match(include_exp, event.key)) and
                            not any(self._match(exclude_exp, event.key))):
                        continue

                    filename = event.key
                    if os.path.isfile(filename):
                        with open(filename, 'rb') as f:
                            content = f.read()
                            md5 = hashlib.md5(content).hexdigest()
                            mime_type = mime.id_buffer(content)
                            file_encoding = encoding.id_buffer(content)
                            state = self.new_state(key=filename,
                                                   md5=md5,
                                                   mime_type=mime_type,
                                                   encoding=file_encoding,
                                                   content=content)
                        yield from self.hub.put(state)
