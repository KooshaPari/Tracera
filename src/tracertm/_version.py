"""Version and early env setup (must run before any pydantic import)."""

import os

os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "logfire-plugin")

__version__ = "0.1.0"
__author__ = "BMad"
