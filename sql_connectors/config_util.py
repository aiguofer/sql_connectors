# -*- coding: utf-8 -*-


__all__ = ["get_key_value", "set_key_value"]


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
