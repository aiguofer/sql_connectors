import os

from traitlets import HasTraits, Instance, TraitError, Unicode, default

from .config_util import import_class
from .storage import Storage


class CustomInstance(Instance):
    def validate(self, obj, proposal):
        try:
            return import_class(proposal)(obj.path_or_uri)
        except Exception as e:
            self._error = e.message
            self.error(obj, proposal)

    def error(self, obj, proposal):
        raise TraitError(self._error)


class Config(HasTraits):
    backend_storage = CustomInstance(Storage)
    path_or_uri = Unicode()

    @default("path_or_uri")
    def _default_path_or_uri(self):
        return os.environ.get("SQL_CONNECTORS_PATH_OR_URI", "~/.config/sql_connectors")

    @default("backend_storage")
    def _default_backend_storage(self):
        return os.environ.get(
            "SQL_CONNECTORS_STORAGE", "sql_connectors.storage.LocalStorage"
        )
