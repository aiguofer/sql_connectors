# -*- coding: utf-8 -*-

from builtins import input, str, open

from getpass import getpass
import os
import json
from glob import glob

from .exceptions import ConfigurationException

__all__ = [
    'parse_config',
    'full_path',
    'get_available_configs',
    'get_available_envs_factory',
    'prompt_creds',
    'get_key_value',
    'set_key_value'
]

CONFIG_BASE_DIR = os.environ.get('SQL_CONNECTORS_CONFIG_DIR',
                                 os.path.expanduser("~/.config/sql_connectors"))

def parse_config(conf, env):
    """Get the specific environment and expand any relative paths

    :param str conf: Name of config file without the file extension
    :param str env: Name of the environment within the config file
    """
    relative_paths = conf.get('relative_paths', [])

    if env not in conf:
        raise ConfigurationException('Env does not exist in config file')

    env_conf = conf[env]

    if not env_conf.get('username', None) or \
       not env_conf.get('password', None):
        env_conf['username'], env_conf['password'] = prompt_creds()

    for rel_path in relative_paths:
        sub_path = get_key_value(env_conf, rel_path)
        set_key_value(env_conf, rel_path, full_path(sub_path))

    env_conf['drivername'] = conf.get('drivername', None)

    return env_conf


def full_path(sub_path):
    """Turn a path relative to the config base dir into a full path

    :param str sub_path: Subpath relative to the config base dir
    """
    return os.path.join(CONFIG_BASE_DIR, sub_path)


def get_available_configs():
    """Return available config file names with their default values as a
    list of tuples like (file_name, default_value_dict)
    """
    files = glob(full_path("*.json"))
    return [(f.split('/')[-1].replace('.json', ''), _get_config_defaults(f))
            for f in files]


def _get_config_defaults(path):
    """Return the default_env, default_schema, and default_reflect from a
    config file.

    :param str path: Path for config file
    """
    defaults = {
        'default_env': 'default',
        'default_schema': 'public',
        'default_reflect': False
    }
    try:
        with open(path) as reader:
            conf = json.load(reader)
            return dict((k, conf.get(k, defaults[k])) for k in defaults)
    except IOError:
        raise ConfigurationException('Config file not found')


def get_available_envs_factory(config_file):
    """Create a :any:`get_available_envs` function for the given config
    file.

    :param str config_file: Name of config file without the file extension
    """
    def get_available_envs():
        """Return available environments in config file"""
        path = full_path(str(config_file) + '.json')
        try:
            with open(path) as reader:
                keys = list(json.load(reader))
                non_envs = ['drivername', 'relative_paths', 'default_env', 'default_schema', 'default_reflect']
                return filter(lambda x: x not in non_envs, keys)
        except IOError:
            raise ConfigurationException('Config file not found')
    return get_available_envs


def prompt_creds(username_prompt='Username: ', password_prompt='Password: '):
    """Prompt user for credentials, returns (username, password)"""
    return input(username_prompt), getpass(password_prompt)


def get_key_value(obj, key):
    """Get value for a nested key using period separated accessor

    :param dict obj: Dict or json-like object
    :param str key: Key, can be in the form of 'key.nestedkey'
    """
    keys = key.split('.')

    if len(keys) == 1:
        return obj.get(keys[0])
    else:
        return get_key_value(obj.get(keys[0]), '.'.join(keys[1:]))


def set_key_value(obj, key, value):
    """Set value for a nested key using period separated accessor

    :param dict obj: Dict or json-like object
    :param str key: Key, can be in the form of 'key.nestedkey'
    :param anything value: The value to be set for the specific key
    """
    keys = key.split('.')

    if len(keys) == 1:
        obj[keys[0]] = value
    else:
        set_key_value(obj.get(keys[0]), '.'.join(keys[1:]), value)
