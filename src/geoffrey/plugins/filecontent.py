"""
The filecontent plugin.

"""
from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
import mimetypes
import asyncio
import hashlib
import json
import os

from bottle import request
from bottle import response
from bottle import HTTPError
import magic

from geoffrey import plugin
from geoffrey.data import datakey
from geoffrey.subscription import subscription


class FileContent(plugin.GeoffreyPlugin):
    """
    The filecontent manages filesystem changes and emit states with
    the file content.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = set()

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

    def configure_app(self):
        self.app.route('/filelist', callback=self.filelist)
        self.app.route('/filetree', callback=self.filetree)
        super().configure_app()


    def filelist(self, *args, **kwargs):
        """List of files."""
        response.content_type = 'application/json'
        return json.dumps(list(self.files))

    def filetree(self, *args, **kwargs):
        """JSON structure for jstree."""
        from pathlib import Path
        response.content_type = 'application/json'

        if not self.files:
            return json.dumps([])

        def elem_from_path(elem, parent):
            id_ = str(elem)

            if elem == parent:
                parent = "#"
                text = str(elem)
            else:
                parent = str(elem.parent)
                text = elem.name

            if elem.is_dir():
                icon = 'glyphicon glyphicon-folder-open'
            elif elem.is_file():
                icon = 'glyphicon glyphicon-file'
            else:
                icon = ""

            return {'id': id_, 'parent': parent, 'text': text, 'icon': icon}

        parent_parts = []
        for parts in zip(*[Path(p).parts for p in self.files]):
            common_parts = list(set(parts))
            if len(common_parts) > 1:
                break
            else:
                parent_parts.append(common_parts[0])
        parent = Path(os.path.join(*parent_parts))

        elements = set([parent])
        for filename in self.files:
            path = Path(filename)
            elements.update([path])
            elements.update([p for p in path.parents if p > parent])

        return json.dumps([elem_from_path(elem, parent=parent) for elem in elements])

    def _match(self, expressions, data):
        for exp in expressions:
            yield fnmatch(data, exp.strip())

    @subscription
    def modified_files(self, event):
        """Filed modified by the user."""
        return (self.project.name == event.project and
                event.plugin == "filesystem" and
                event.fs_event in ("modified", "created"))

    @subscription
    def removed_files(self, event):
        """Removed or moved files."""
        return (self.project.name == event.project and
                event.plugin == "filesystem" and
                event.fs_event in ("deleted", "moved"))

    def get_file_state(self, filename, loop):

        with open(filename, 'rb') as f:
            raw = f.read()

        # Calculate a MD5 hash of the file.
        md5 = hashlib.md5(raw).hexdigest()

        # Get the mime type (extension || libmagic || 'unknown').
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            try:
                with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as mime:
                    mime_type = mime.id_buffer(raw)
            except:
                mime_type = 'unknown'

        # Get the file encoding.
        try:
            with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as encoding:
                file_encoding = encoding.id_buffer(raw)
        except:
            file_encoding = 'unknown'

        # If is a known encoding, decode the binary data.
        python_encoding = self.libmagic_encoding2python(file_encoding)
        try:
            # If is unknown give a try to the most common one.
            if python_encoding is None:
                python_encoding = 'utf-8'  # Give it a try
            content = raw.decode(python_encoding)
        except:
            content = None

        state = self.new_state(task="read_modified_files",
                               key=filename,
                               md5=md5,
                               mime_type=mime_type,
                               encoding=file_encoding,
                               content=content,
                               raw=raw)

        loop.call_soon_threadsafe(self.hub.put_nowait, state)

    @asyncio.coroutine
    def delete_files(self, events:"removed_files") -> plugin.Task:
        while True:
            event = yield from events.get()
            try:
                self.files.remove(event.key)
            except:
                pass
            state = self.new_state(key=event.key)
            yield from self.hub.put(state)

    @asyncio.coroutine
    def read_modified_files(self, events:"modified_files") -> plugin.Task:
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
                    not any(self._match(exclude_exp, event.key)))\
               or os.path.isdir(event.key):
                continue

            filename = event.key
            self.files.update([filename])

            yield from loop.run_in_executor(executors, self.get_file_state,
                                            filename, loop)
