import inspect
import os

from traitlets import HasTraits, Instance, TraitError, Unicode, default

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


def import_class(cl):
    parts = cl.split(".")

    if len(parts) <= 1:
        raise Exception(
            "Fully qualified class name required, only module provided: {}".format(cl)
        )
    class_name = parts[-1]
    module_name = ".".join(parts[0:-1])
    try:
        module = __import__(module_name, globals(), locals(), [class_name])
    except ImportError:
        raise Exception("Couldn't find module: {}".format(module_name))

    try:
        obj = getattr(module, class_name)
        if not inspect.isclass(obj):
            raise Exception(
                "Provided fully qualified name is not a class: {}".format(cl)
            )
        return obj
    except AttributeError:
        raise Exception("Couldn't find class: {}".format(class_name))


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
