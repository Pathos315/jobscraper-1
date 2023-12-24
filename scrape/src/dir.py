from contextlib import contextmanager
from os import chdir, getcwd, makedirs, path


@contextmanager
def change_dir(destination: str):
    """Sets a destination for exported files."""
    cwd = getcwd()
    try:
        __dest = path.realpath(destination)
        makedirs(__dest, exist_ok=True)
        chdir(__dest)
        yield
    finally:
        chdir(cwd)
