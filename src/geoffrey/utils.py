import asyncio
import re
import uuid
import logging

from geoffrey.hub import get_hub
from geoffrey.data import Event


alphanumeric = re.compile(r'[\x80-\xFF(\W+)]')


def write_template(filename, content):
    """ Write content to disk. """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def slugify(text):
    """ Replace all bad characters by `_`. """
    slugified = alphanumeric.sub('_', text.lower().rstrip())
    return slugified


class GeoffreyLoggingHandler(logging.Handler):
    def __init__(self):
        self.hub = get_hub()
        super().__init__()

    def emit(self, record):
        if record.name == 'geoffrey.hub':  # Avoid logging loop
            return

        project = getattr(record, 'project', None)
        plugin = getattr(record, 'plugin', None)
        key = 'logging'
        event = Event(project=project, plugin=plugin, key=key,
                      message=record.getMessage(), level=record.levelname)

        self.hub.put_nowait(event)


@asyncio.coroutine
def execute(*args, stdin=None, **kwargs):
    """
    Return the result of an external command execution.

    """
    from asyncio import subprocess

    subexec = asyncio.create_subprocess_exec
    proc = yield from subexec(*args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              **kwargs)
    try:
        stdout, stderr = yield from proc.communicate(stdin)
    except:
        proc.kill()
        yield from proc.wait()
        raise
    exitcode = yield from proc.wait()
    return (exitcode, stdout, stderr)
