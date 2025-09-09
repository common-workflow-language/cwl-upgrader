"""Shared test utility functions."""

import atexit
import os
import shutil
from contextlib import ExitStack
from importlib.resources import as_file, files
from pathlib import Path


def get_path(filename: str) -> Path:
    """Get the file Path for a given test file."""
    # normalizing path depending on OS or else it will cause problem when joining path
    filename = os.path.normpath(filename)
    filepath = None
    try:
        file_manager = ExitStack()
        atexit.register(file_manager.close)
        traversable = files("cwlupgrader") / filename
        filepath = file_manager.enter_context(as_file(traversable))
    except ModuleNotFoundError:
        pass
    if not filepath or not filepath.is_file():
        filepath = Path(os.path.dirname(__file__), os.pardir, filename)
    return filepath.resolve()


def get_data(filename: str) -> str:
    """Get the filename as string for a given test file."""
    return str(get_path(filename))
