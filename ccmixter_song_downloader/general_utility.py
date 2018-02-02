import unicodedata
import re
import os


def slugify(value):
    """Normalizes string, removes characters that are not:
    alphanumeric, whitespace, or dash characters"""
    # taken from http://stackoverflow.com/a/295466
    # with some modification
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub(r'[^\w\s-]', '', value.decode('ascii')).strip())
    return value


def create_directories_if_needed(path, is_file=True):
    path = os.path.abspath(path)
    if is_file:
        path = os.path.dirname(path)
    if not os.path.isdir(path):
        os.makedirs(path)