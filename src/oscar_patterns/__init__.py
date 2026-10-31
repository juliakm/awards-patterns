"""Reusable Python tools for Awards Patterns."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("oscar-patterns")
except PackageNotFoundError:
    # Source-tree imports are useful before the editable environment is restored.
    __version__ = "0.1.0"
