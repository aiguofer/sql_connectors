import os
from argparse import Namespace
from builtins import super
from glob import glob
from memoized import memoized
from .util import extend_docs
import json

from six import iteritems

from .client import SqlClient, get_client_factory
from .config_util import full_path, get_available_configs, get_available_envs_factory
from .exceptions import ConfigurationException

DEFAULT_CONFIG_DIR = "~/.config/sql_connectors"

CONFIG_DEFAULTS = {
    "default_env": "default",
    "default_schema": None,
    "default_reflect": False,
}
NON_ENV_KEYS = [
    "drivername",
    "relative_paths",
    "allowed_hosts",
    "default_env",
    "default_schema",
    "default_reflect",
]


def merge_dicts(*args):
    # should raise warning for duplicate keys
    res_dict = {}
    for d in args:
        for k, v in iteritems(d):
            res_dict[k] = v
    return res_dict


def read_json(fpath):
    try:
        with open(fpath) as reader:
            config = json.load(reader)
            return config
    except IOError:
        raise ConfigurationException("Config file not found")


def full_path(sub_path="", default_config_dir=DEFAULT_CONFIG_DIR):
    """Turn a path relative to the config base dir into a full path

    :param str sub_path: Subpath relative to the config base dir
    """
    config_base_dir = os.environ.get('SQL_CONNECTORS_CONFIG_DIR',
                                     default_config_dir)

    return os.path.join(os.path.expanduser(config_base_dir), sub_path)


def get_available_configs(fpath):
    files = glob(os.path.join(fpath, "*.json"))
    return files


class ParseConfig(object):
    def __init__(self, fname, config_dict=None, config_path=None):
        self.fname = fname
        self.config = config_dict
        self.config_path = config_path

    @staticmethod
    def read_config_file(fname, config_path=None):
        if isinstance(fname, str):
            fpath = full_path(fname + ".json", config_path)
            config = read_json(fpath)
        else:
            raise ConfigurationException(
                "Invalid config object - must be filename (no extension)"
            )
        return config

    @staticmethod
    def get_config_defaults(config, defaults=CONFIG_DEFAULTS):
        return dict((k, config.get(k, defaults[k])) for k in defaults.keys())

    @staticmethod
    def get_client_factory_kwargs(fname, defaults=CONFIG_DEFAULTS, config_dict=None, config_path=None):
        if config_dict:
            config = config_dict
        else:
            config = ParseConfig.read_config_file(fname, config_path)
        config_defaults = ParseConfig.get_config_defaults(config, defaults)
        kwargs = merge_dicts({"config": config}, config_defaults)
        return kwargs

    @extend_docs(SqlClient.__init__)
    @staticmethod
    def get_client_factory(**kwargs):
        for key in ["config", "default_env", "default_schema", "default_reflect"]:
            assert key in kwargs.keys(), "{0} must be a kwarg".format(key)
        NS = Namespace(**kwargs)
        def get_client(
            env=NS.default_env,
            default_schema=NS.default_schema,
            reflect=NS.default_reflect,
            **kwargs
        ):
            return SqlClient(NS.config, env, default_schema, reflect, **kwargs)

        return memoized(get_client, signature_preserving=True)

    def get_available_envs(self, non_env_keys=NON_ENV_KEYS):
        if not self.config:
            self.config = self.read_config_file(self.fname, self.config_path)
        keys = list(self.config.keys())
        return [i for i in keys if i not in non_env_keys]

    def get_factory_dict(self):
        if not self.config:
            self.config = self.read_config_file(self.fname, self.config_path)
        factory_kwargs = self.get_client_factory_kwargs(
            self.fname, config_dict=self.config
        )
        factory = self.get_client_factory(**factory_kwargs)
        return {self.fname: factory, self.fname + "_envs": self.get_available_envs()}


class BuildFacade(object):
    def __init__(self, config_params, mode="file", **kwargs):
        # Need another class to dynamically generate "config params" for file vs redis
        assert mode in [
            "file",
            "redis",
        ], "Invalid config parsing mode {0} specified".format(mode)
        self.config_params = config_params
        self.config_path = kwargs.get("config_path", None)

    def get_factories(self):
        factory_args = []
        for params in self.config_params:
            name = params["name"]
            config = params.get("config_dict", None)
            parser = ParseConfig(name, config, self.config_path)
            factory_args.append(parser.get_factory_dict())
        return merge_dicts(*factory_args)

    def build_factory_facade(self):
        kwargs = self.get_factories()
        instance = Namespace(**kwargs)
        return instance


def default_facade(**kwargs):
    cls = BuildFacade(**kwargs)
    return cls.build_factory_facade()
