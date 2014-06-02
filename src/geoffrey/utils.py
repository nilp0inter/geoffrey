import re
import uuid

alphanumeric = re.compile(r'[\x80-\xFF(\W+)]')


def write_template(filename, content):
    """ Write content to disk. """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def slugify(text):
    """ Replace all bad characters by `_`. """
    slugified = alphanumeric.sub('_', text.lower().rstrip())
    return slugified
