# -*- coding: utf-8 -*-

from builtins import input, str, open

from getpass import getpass
import os
import json
from glob import glob

from sqlalchemy.engine.url import URL

from .exceptions import ConfigurationException

__all__ = [
    'parse_config',
    'full_path',
    'get_available_configs',
    'get_available_envs_factory',
    'get_key_value',
    'set_key_value'
]

DEFAULT_CONFIG_DIR = "~/.config/sql_connectors"

def parse_config(conf, env):
    """Get the specific environment, expand any relative paths, and return
    a url for create_engine

    :param str conf: Name of config file without the file extension
    :param str env: Name of the environment within the config file
    """
    if env not in conf:
        raise ConfigurationException('Env does not exist in config file')

    if 'drivername' not in conf:
        raise ConfigurationException('Missing drivername')

    drivername = conf['drivername']

    env_conf = conf[env]
    env_conf['drivername'] = drivername

    for rel_path in conf.get('relative_paths', []):
        sub_path = get_key_value(env_conf, rel_path)
        set_key_value(env_conf, rel_path, full_path(sub_path))

    if 'sqlite' not in drivername:
        env_conf['username'] = _get_username(env_conf)

        env_conf['password'] = _get_password(env_conf)

        env_conf.pop('allowed_hosts', [])

    return URL(**env_conf)


def full_path(sub_path):
    """Turn a path relative to the config base dir into a full path

    :param str sub_path: Subpath relative to the config base dir
    """
    config_base_dir = os.environ.get('SQL_CONNECTORS_CONFIG_DIR',
                                     DEFAULT_CONFIG_DIR)

    return os.path.join(os.path.expanduser(config_base_dir), sub_path)


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
        'default_schema': None,
        'default_reflect': False
    }
    try:
        with open(path) as reader:
            conf = json.load(reader)
            return dict((k, conf.get(k, defaults[k])) for k in defaults)
    except IOError:
        raise ConfigurationException('Config file not found')
    except:
        raise ConfigurationException('Error reading {0}'.format(path))


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
                non_envs = ['drivername', 'relative_paths', 'allowed_hosts',
                            'default_env', 'default_schema', 'default_reflect']
                return [key for key in keys if key not in non_envs]
        except IOError:
            raise ConfigurationException('Config file not found')
    return get_available_envs


def _get_username(conf):
    """Get username and prompt user if necessary. Set to None if it's empty."""
    username = conf.get('username', None)
    allowed_hosts = conf.get('allowed_hosts', [])
    if username is None or (len(allowed_hosts) > 0 and not os.uname()[1] in allowed_hosts):
        username = input('Username: ')
    if username == '':
        username = None
    return username


def _get_password(conf):
    """Get password and prompt user if necessary. Set to None if it's empty."""
    password = conf.get('password', None)
    allowed_hosts = conf.get('allowed_hosts', [])
    if password is None or (len(allowed_hosts) > 0 and not os.uname()[1] in allowed_hosts):
        password = getpass('Password: ')
    if password == '':
        password = None
    return password


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
