"""
The filecontent plugin.

"""
import asyncio
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch

import magic

from geoffrey import plugin
from geoffrey.subscription import subscription


class FileContent(plugin.GeoffreyPlugin):
    """
    The filecontent manages filesystem changes and emit states with
    the file content.

    """
    @staticmethod
    def libmagic_encoding2python(file_encoding):
        if file_encoding == 'us-ascii':
            python_encoding = 'ascii'
        elif file_encoding == 'utf-8':
            python_encoding = 'utf-8'
        elif file_encoding == 'utf-16le':
            python_encoding = 'utf-16-le'
        elif file_encoding == 'utf-16be':
            python_encoding = 'utf-16-be'
        elif file_encoding == "iso-8859-1":
            python_encoding = 'latin1'
        else:
            python_encoding = None
        return python_encoding

    def _match(self, expressions, data):
        for exp in expressions:
            yield fnmatch(data, exp.strip())

    @subscription
    def modified_files(event):
        """Filed modified by the user."""
        return (event.plugin == "filesystem" and
                event.fs_event in ("modified", "created"))


    def get_file_state(self, filename, loop):
       with open(filename, 'rb') as f:
           raw = f.read()

       md5 = hashlib.md5(raw).hexdigest()

       try:
           with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as mime:
               mime_type = mime.id_buffer(raw)
       except:
           mime_type = 'unknown'

       try:
           with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as encoding:
               file_encoding = encoding.id_buffer(raw)
       except:
           file_encoding = 'unknown'

       python_encoding = self.libmagic_encoding2python(file_encoding)
       try:
           if python_encoding is None:
               python_encoding = 'utf-8'  # Give it a try
           content = raw.decode(python_encoding)
       except:
           content = None

       state = self.new_state(key=filename,
                              md5=md5,
                              mime_type=mime_type,
                              encoding=file_encoding,
                              content=content,
                              raw=raw)
       loop.call_soon_threadsafe(self.hub.put_nowait, state)


    @asyncio.coroutine
    def read_modified_files(self, events: modified_files) -> plugin.Task:
        loop = asyncio.get_event_loop()
        try:
            workers = self.config.getint(self._section_name, 'parallel')
        except:
            workers = 32

        executors = ThreadPoolExecutor(max_workers=workers)

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

        while True:

            event = yield from events.get()

            if not (any(self._match(include_exp, event.key)) and
                    not any(self._match(exclude_exp, event.key))):
                continue

            filename = event.key
            if os.path.isfile(filename):
                yield from loop.run_in_executor(executors, self.get_file_state,
                                                filename, loop)
