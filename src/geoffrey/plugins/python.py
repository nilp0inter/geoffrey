import logging
import subprocess
import asyncio
from asyncio import subprocess
from geoffrey import plugin
from geoffrey.event import Event
from geoffrey.state import State
from geoffrey.subscription import subscription
from watchdog.events import EVENT_TYPE_MODIFIED

logger = logging.getLogger(__name__)

def python_file_changes(data):
    return (isinstance(data, Event) and
            data.type == EVENT_TYPE_MODIFIED and
            data.key.endswith(b'.py'))

sub = subscription(filter_func=python_file_changes)

class PyLint(plugin.GeoffreyPlugin):
    @asyncio.coroutine
    def run_pylint(self, changes: sub) -> plugin.Task:
        while True:
            event = yield from changes.get()
            filename = event.key
            proc = yield from asyncio.create_subprocess_exec(
                    "pylint", filename, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            try:
                stdout, _ = yield from proc.communicate()
            except:
                proc.kill()
                yield from proc.wait()
                raise
            exitcode = yield from proc.wait()

            state = State(object=filename, namespace='metrics', exitcode=exitcode, stdout=stdout)
            logger.debug("Putting state %r", state)
            yield from self.hub.put(state)
