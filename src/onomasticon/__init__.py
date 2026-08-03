"""
Public package exports for onomasticon.
"""

from ._version import __version__, get_version
from .onomasticon import ImplementationRegistry, ImplementationT

__all__ = [
    "ImplementationRegistry",
    "ImplementationT",
    "__version__",
    "get_version",
]
