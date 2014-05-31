import re
import uuid

alphanumeric = re.compile(r'[\x80-\xFF(\W+)]')


def write_template(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def slugify(text):
    slugified = alphanumeric.sub('_', text.lower().rstrip())
    return slugified
