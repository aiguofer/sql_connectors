# -*- coding: utf-8 -*-
import inspect

__all__ = ["get_key_value", "set_key_value", "import_class"]


def get_key_value(obj, key):
    """Get value for a nested key using period separated accessor

    :param dict obj: Dict or json-like object
    :param str key: Key, can be in the form of 'key.nestedkey'
    """
    keys = key.split(".")

    if len(keys) == 1:
        return obj.get(keys[0])
    else:
        return get_key_value(obj.get(keys[0]), ".".join(keys[1:]))


def set_key_value(obj, key, value):
    """Set value for a nested key using period separated accessor

    :param dict obj: Dict or json-like object
    :param str key: Key, can be in the form of 'key.nestedkey'
    :param anything value: The value to be set for the specific key
    """
    keys = key.split(".")

    if len(keys) == 1:
        obj[keys[0]] = value
    else:
        set_key_value(obj.get(keys[0]), ".".join(keys[1:]), value)


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
