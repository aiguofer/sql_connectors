# -*- coding: utf-8 -*-

import os

from ._version import __version__, __version_info__
from .storage import LocalStorage

__all__ = ["__version__", "__version_info__", "LocalStorage", "default_connections"]

DEFAULT_PATH_OR_URI = os.environ.get(
    "SQL_CONNECTORS_PATH_OR_URI", "~/.config/sql_connectors"
)

DEFAULT_STORAGE = os.environ.get("SQL_CONNECTORS_STORAGE", "local")

storage_backends = {"local": LocalStorage}

default_backend = storage_backends[DEFAULT_STORAGE]
default_connections = default_backend(DEFAULT_PATH_OR_URI).connections
