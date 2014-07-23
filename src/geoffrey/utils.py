"""
Utility function and classes.

"""
#pylint: disable=I0011,E1101
import asyncio
import re
import logging
import json

from xml.etree import ElementTree

from geoffrey.hub import get_hub
from geoffrey.data import Event


ALPHANUMERIC = re.compile(r'[\x80-\xFF(\W+)]')


def write_template(filename, content):
    """ Write content to disk. """
    with open(filename, 'w', encoding='utf-8') as file_:
        file_.write(content)


def slugify(text):
    """ Replace all bad characters by `_`. """
    slugified = ALPHANUMERIC.sub('_', text.lower().rstrip())
    return slugified


class GeoffreyLoggingHandler(logging.Handler):
    """Use the Geoffrey infraestructure as a logging handler."""
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


jsonencoder = json.JSONEncoder(skipkeys=True, default=lambda o: None)


def get_api(app_routes, prefix):
    """ Return a list of endpoints for documentation. """
    from cgi import escape
    routes = {escape(route.rule)
              for route in app_routes
              if route.rule.startswith(prefix)}
    html_list = '<ul>'
    for route in sorted(routes):
        html_list += '<li>{}</li>'.format(route)
    html_list += '</ul>'
    return html_list


def parse_checkstyle(stdout):
    tree = ElementTree.fromstring(stdout)
    if not tree:
        return []
    filetag = tree.find('file')
    errors = []
    for error in filetag.getchildren():
        error_data = {}
        for item, value in error.items():
            if value.isnumeric():
                error_data[item] = int(value)
            else:
                error_data[item] = value
        errors.append(error_data)
    return errors
