from __future__ import unicode_literals

import json
import os
from builtins import bytes, open, super
from getpass import getpass
from glob import glob
from warnings import warn

from future.utils import iteritems
from memoized import memoized
from six.moves import input
from sqlalchemy.engine.url import URL

from .client import SqlClient
from .config_util import get_key_value, set_key_value
from .exceptions import ConfigurationException, SQLConnectorException
from .util import extend_docs

__all__ = ["Storage", "LocalStorage"]


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        # this breaks autocompletion
        raise SQLConnectorException("Connection {} does not exist".format(name))

    def __dir__(self):
        # fix autocompletion due to __getattr__
        return self.__dict__.keys()


class Storage(object):
    def __init__(self, path_or_uri):
        self._path_or_uri = path_or_uri

        configs = self._fetch_configs()

        connections = {}
        for name, conf in iteritems(configs):
            if isinstance(name, bytes):
                name = name.decode("utf8")
            defaults = self._get_config_defaults(conf)
            env_getter = self._get_available_envs_factory(conf)
            schema = defaults["default_schema"]

            client_getter = self._get_client_factory(
                conf,
                defaults["default_env"],
                '"{0}"'.format(schema) if schema is not None else schema,
                defaults["default_reflect"],
            )
            connections["{}".format(name)] = client_getter
            connections["{}_envs".format(name)] = env_getter

        self.connections = Namespace(**connections)

    def _fetch_configs(self):
        raise NotImplementedError

    def _parse_config(self, conf, env):
        """Get the specific environment, expand any relative paths, and return
        a url for create_engine

        :param str conf: Name of config file without the file extension
        :param str env: Name of the environment within the config file
        """
        if env not in conf:
            raise ConfigurationException("Env does not exist in config file")

        if "drivername" not in conf:
            raise ConfigurationException("Missing drivername")

        drivername = conf["drivername"]

        env_conf = conf[env]
        env_conf["drivername"] = drivername

        if "sqlite" not in drivername:
            env_conf["username"] = self._get_username(env_conf)

            env_conf["password"] = self._get_password(env_conf)

            env_conf.pop("allowed_hosts", [])

        return URL(**env_conf)

    def _get_available_envs_factory(self, conf):
        """Create a :any:`get_available_envs` function for the given config
        file.

        :param str config_file: Name of config file without the file extension
        """

        def get_available_envs():
            """Return available environments in config file"""
            keys = list(conf)
            non_envs = [
                "drivername",
                "relative_paths",
                "allowed_hosts",
                "default_env",
                "default_schema",
                "default_reflect",
            ]
            return [key for key in keys if key not in non_envs]

        return get_available_envs

    def _get_username(self, conf):
        """Get username and prompt user if necessary. Set to None if it's empty."""
        username = conf.get("username", None)
        allowed_hosts = conf.get("allowed_hosts", [])
        if username is None or (
            len(allowed_hosts) > 0 and not os.uname()[1] in allowed_hosts
        ):
            username = input("Username: ")
        if username == "":
            username = None
        return username

    def _get_password(self, conf):
        """Get password and prompt user if necessary. Set to None if it's empty."""
        password = conf.get("password", None)
        allowed_hosts = conf.get("allowed_hosts", [])
        if password is None or (
            len(allowed_hosts) > 0 and not os.uname()[1] in allowed_hosts
        ):
            password = getpass("Password: ")
        if password == "":
            password = None
        return password

    def _get_config_defaults(self, conf):
        """Return the default_env, default_schema, and default_reflect from a
        config file.

        :param str path: Path for config file
        """
        defaults = {
            "default_env": "default",
            "default_schema": None,
            "default_reflect": False,
        }
        return dict((k, conf.get(k, defaults[k])) for k in defaults)

    def _get_client_factory(
        self, conf, default_env="default", default_schema=None, default_reflect=False
    ):
        """Wrapper function to create a :any:`get_client` function using the given
        ``config`` and setting the given defaults. This should be used in the submodule
        for each data source.

        :param str conf: Name of config file without the extension
        :param str default_env: Set default environment to use (Default value = 'default')
        :param str default_schema: Set default schema to use  (Default value = None)
        :param bool default_reflect: Set default for reflect  (Default value = False)
        """

        @extend_docs(SqlClient.__init__)
        def get_client(
            env=default_env,
            default_schema=default_schema,
            reflect=default_reflect,
            **kwargs
        ):
            """Get a :any:`SqlClient` for the specified
            environment. Defaults are based on what was passed to :any:`get_client_factory`.

            See :any:`SqlClient.__init__` for params:
            """
            return SqlClient(
                self._parse_config(conf, env), default_schema, reflect, **kwargs
            )

        return memoized(get_client, signature_preserving=True)


class LocalStorage(Storage):
    def __init__(self, path_or_uri):
        super().__init__(path_or_uri)

    def _full_path(self, sub_path):
        """Turn a path relative to the config base dir into a full path

        :param str sub_path: Subpath relative to the config base dir
        """
        return os.path.join(os.path.expanduser(self._path_or_uri), sub_path)

    def _check_path(self):
        """Check if the provided path exists. If not, raise ConfigurationException.
        """
        path = os.path.dirname(self._full_path(""))

        if not os.path.exists(path):
            raise ConfigurationException("Config dir {} not found".format(path))

    def _fetch_configs(self):
        """Return available config file names with their default values as a
        list of tuples like (file_name, default_value_dict)
        """
        self._check_path()

        files = glob(self._full_path("*.json"))

        confs = {}
        for f in files:
            try:
                name = f.split("/")[-1].replace(".json", "")
                conf = self._read_json(f)
                for rel_path in conf.get("relative_paths", []):
                    for env in self._get_available_envs_factory(conf)():
                        sub_path = get_key_value(conf[env], rel_path)
                        set_key_value(conf[env], rel_path, self._full_path(sub_path))

                confs[name] = conf
            except ConfigurationException as e:
                warn(e.message)

        return confs

    def _read_json(self, path):
        """Return the default_env, default_schema, and default_reflect from a
        config file.

        :param str path: Path for config file
        """
        try:
            with open(path) as reader:
                return json.load(reader)
        except IOError:
            raise ConfigurationException("Config file not found")
        except ValueError as e:
            raise ConfigurationException("Error reading {0}:\n{1}".format(path, e))
