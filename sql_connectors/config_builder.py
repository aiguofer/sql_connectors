import os
from argparse import Namespace
from builtins import super
from glob import glob

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


def read_json(fname):
    try:
        with open(path) as reader:
            conf = json.load(reader)

            return parse_config(conf, self.env)
    except IOError:
        raise ConfigurationException("Config file not found")


def get_available_configs(fpath):
    files = glob(os.path.join(fpath, "*.json"))
    return files


class ParseConfig(object):
    def __init__(self, fname, config_dict=None):
        self.fname = fname
        self.config = None

    @staticmethod
    def read_config_file(fname):
        if isinstance(fname, str):
            fpath = full_path(fname + ".json")
            config = read_json(fpath)
        else:
            raise ConfigurationException(
                "Invalid config object - must be filename (no extension)"
            )
        return config

    @staticmethod
    def get_config_defaults(config, defaults=CONFIG_DEFAULTS):
        for key in ["default_env", "default_schema", "default_reflect"]:
            assert key in config.keys(), "{0} must be in your config defaults dict - "
        return dict((k, config.get(k, defaults[k])) for k in defaults)

    @staticmethod
    def get_client_factory_kwargs(fname, defaults=CONFIG_DEFAULTS, config_dict=None):
        if config_dict:
            config = config_dict
        else:
            config = ParseConfigs.read_config_file(fname)
        config_defaults = ParseConfigs.get_config_defaults(config, defaults)
        kwargs = merge_dicts({"config": config}, config_defaults)
        return kwargs

    @staticmethod
    @extend_docs(SqlClient.__init__)
    def get_client_factory(**kwargs):
        for key in ["config", "default_env", "default_schema", "default_reflect"]:
            assert kwargs.get(key, None), "{0} must be a kwarg"
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
            self.config = self.read_config_file(self.fname)
        keys = list(self.config.keys())
        return [i for i in keys if i not in non_env_keys]

    def get_factory_dict(self):
        if not self.config:
            self.config = self.read_config_file(self.fname)
        factory_kwargs = self.get_client_factory_kwargs(
            self.fname, config_dict=self.config
        )
        factory = self.get_client_factory(**factory_kwargs)
        return {self.fname: factory, self.fname + "_envs": self.get_available_envs()}


class BuildFacade(object):
    def __init__(self, config_param_dict, mode="file", **kwargs):
        # Need another class to dynamically generate "config params" for file vs redis
        assert mode in [
            "file",
            "redis",
        ], "Invalid config parsing mode {0} specified".format(mode)
        self.config_param_dict = config_param_dict

    def get_factories(self):
        factory_args = []
        for params in self.config_param_dict:
            name = params["name"]
            config = params.get("config_dict", None)
            parser = ParseConfig(name, config)
            factory_args.append(factory_dict)
        return merge_dicts(*factory_args)

    def build_factory_facade(self):
        kwargs = self.get_factories
        instance = Namespace(**kwargs)
        return instance


def default_facade(**kwargs):
    cls = BuildFacade(**kwargs)
    return cls.build_factory_facade()
