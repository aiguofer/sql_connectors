def setup():
    import os

    def import_class(cl):
        last_dot = cl.rfind(".")
        class_name = cl[last_dot + 1 : len(cl)]
        module_name = cl[0:last_dot]
        try:
            module = __import__(module_name, globals(), locals(), [class_name])
        except ImportError:
            raise Exception("Couldn't find module: {}".format(module_name))

        try:
            return getattr(module, class_name)
        except AttributeError:
            raise Exception("Couldn't find class: {}".format(class_name))

    DEFAULT_PATH_OR_URI = os.environ.get(
        "SQL_CONNECTORS_PATH_OR_URI", "~/.config/sql_connectors"
    )

    DEFAULT_STORAGE = os.environ.get(
        "SQL_CONNECTORS_STORAGE", "sql_connectors.storage.LocalStorage"
    )

    default_backend = import_class(DEFAULT_STORAGE)
    default_connections = default_backend(DEFAULT_PATH_OR_URI)

    globals().update(default_connections.__dict__)
    del globals()["setup"]


setup()
