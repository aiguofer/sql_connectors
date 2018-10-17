import json
import os
from argparse import Namespace
from builtins import super
from glob import glob

from memoized import memoized
from six import iteritems

from .client import SqlClient
from .config_util import full_path
from .exceptions import ConfigurationException
from .util import extend_docs

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
    """Merges takes dicts passed in as individual *args and merges them together
    
    Parameters
    ----------
    *args
        dict

    Raises
    ------
    warning
        [description]
    
    Returns
    -------
    res_dict: dict
    """
    # should raise warning for duplicate keys
    res_dict = {}
    for d in args:
        for k, v in iteritems(d):
            res_dict[k] = v
    return res_dict


def read_json(fpath):
    """Attemps to read a JSON file
    
    Parameters
    ----------
    fpath : str
        full JSON file path
    
    Raises
    ------
    ConfigurationException
        For invalid paths
    
    Returns
    -------
    dict
    """
    try:
        with open(fpath) as reader:
            config = json.load(reader)
            return config
    except IOError:
        raise ConfigurationException("Config file not found")


def full_path(sub_path="", config_dir=None, default_config_dir=DEFAULT_CONFIG_DIR):
    """Turn a path relative to the config base dir into a full path

    Parameters
    ----------
    sub_path: str, optional
        Subpath relative to the config base dir
    config_dir: str, optional
        optional path of config files on disk to override the SQL_CONNECTORS_CONFIG_DIR environment var
    default_config_dir: str, optional
        default config directory to read from if SQL_CONNECTORS_CONFIG_DIR does not exist

    Returns
    ------
    str
    """
    if config_dir:
        config_base_dir = config_dir
    else:
        config_base_dir = os.environ.get("SQL_CONNECTORS_CONFIG_DIR", default_config_dir)
    return os.path.join(os.path.expanduser(config_base_dir), sub_path)


def get_available_configs(fpath=None):
    """Gets all available json configs in a certain path
    
    Parameters
    ----------
    fpath : str
        full file path
    
    Returns
    -------
    list of str
        list of json full file paths
    """
    if fpath is None:
        fpath = full_path()
    files = glob(os.path.join(fpath, "*.json"))
    return files


class ParseConfig(object):
    def __init__(self, fname, config_dict=None, config_path=None):
        """Class to generate a sqlalchemy Engine factory by parsing an individual configuration
        
        Parameters
        ----------
        object : [type]
            [description]
        fname : str
            name of the config file
        config_dict : dict, optional
            optionally pass in a dict object if you want to integrate a config that is not stored
            on disk (i.e a redis config)
        config_path : str, optional
            optionally manually set the full path of the config files
        """
        self.fname = fname
        self.config = config_dict
        self.config_path = config_path

    @staticmethod
    def read_config_file(fname, config_path=None):
        """Reads in a config file from disk
        
        Parameters
        ----------
        fname : str
            file name without extension
        config_path : str, optional
            location of the file on disk (defaults to SQL_CONNECTORS_CONFIG_DIR on $PATH)
        
        Raises
        ------
        ConfigurationException
            If invalid fname
        
        Returns
        -------
        dict
        """
        if isinstance(fname, str):
            fpath = full_path(fname + ".json", config_dir = config_path)
            config = read_json(fpath)
        else:
            raise ConfigurationException(
                "Invalid config object - must be filename (no extension)"
            )
        return config

    @staticmethod
    def get_config_defaults(config, defaults=CONFIG_DEFAULTS):
        """Parses default values from the config dict
        
        Parameters
        ----------
        config : dict
            config dict read in from the config JSON
        defaults : dict, optional
            default engine parameters to fill in if they are not present in the config dict

        Returns
        -------
        dict
        """
        return dict((k, config.get(k, defaults[k])) for k in defaults.keys())

    @staticmethod
    def get_client_factory_kwargs(
        fname, defaults=CONFIG_DEFAULTS, config_dict=None, config_path=None
    ):
        """Gets **kwargs needed to generate the engine factory
        
        Parameters
        ----------
        fname : str
            name of the config file - will be used to set the engine factory name
        defaults : dict, optional
            default engine parameters to fill in if they are not present in the config dict
        config_dict : dict, optional
            optional config dict to skip reading config from disk
        config_path : str, optional
            optional path of config files on disk to override the SQL_CONNECTORS_CONFIG_DIR environment var
        
        Returns
        -------
        dict
        """
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
        """Wrapper function to create a `get_client` function using the given `config_file`
        and setting the given defaults.

        Parameters
        ----------
        **kwargs
            config: dict
                config JSON read in as a dict
            default_env: str
                default environment to set in the sqlalchemy.engine (Default value = 'default')
            default_schema: str
                default schema to set in the sqlalchemy.engine (Default value = None)
            default_reflect: bool
                default reflect to set (Default value = False)

        Returns
        -------
        function
            instance of `get_client`
        """
        for key in ["config", "default_env", "default_schema", "default_reflect"]:
            assert key in kwargs.keys(), "{0} must be a kwarg".format(key)
        NS = Namespace(**kwargs)

        def get_client(
            env=NS.default_env,
            default_schema=NS.default_schema,
            reflect=NS.default_reflect,
            **kwargs
        ):
            """get any `SqlClient` for the specified environment. Defaults are based on what was 
            passed in as **kwargs to `get_client_factory`
            
            Parameters
            ----------
            See `SqlClient.__init__` for params
            """
            return SqlClient(NS.config, env, default_schema, reflect, **kwargs)

        return memoized(get_client, signature_preserving=True)

    def get_available_envs(self, non_env_keys=NON_ENV_KEYS):
        """Parses the config dict for all available environments
        
        Parameters
        ----------
        non_env_keys : list of str, optional
            list of potential config keys that do not correspond to an environment
        
        Returns
        -------
        list
            list of available environments
        """
        if not self.config:
            self.config = self.read_config_file(self.fname, self.config_path)
        keys = list(self.config.keys())
        return [i for i in keys if i not in non_env_keys]

    def get_factory_dict(self):
        """Returns a dict containing the factory method names along with the corresponding functions
        
        Returns
        -------
        dict:
            key: {fname}, value: get_client instance
            key: {fname}_envs, value: available environments from client
        """
        if not self.config:
            self.config = self.read_config_file(self.fname, self.config_path)
        factory_kwargs = self.get_client_factory_kwargs(
            self.fname, config_dict=self.config
        )
        factory = self.get_client_factory(**factory_kwargs)
        return {self.fname: factory, self.fname + "_envs": self.get_available_envs()}


class BuildFacade(object):
    def __init__(self, config_params, **kwargs):
        """Builds an isolated namespace containing all SqlClient factory and environment
        objects parsed from a set of config params
        
        Parameters
        ----------
        config_params : tuple of dicts
            tuple of dicts with the following format
            key: "name", value: {name of desired factory function}
            and an optional...
            key: "config_dict", value: dict
            if there name does not correspond to a location on disk
        
        **kwargs
        config_path: str
            optional path of config files on disk to override the SQL_CONNECTORS_CONFIG_DIR environment var
        """
        self.config_params = config_params
        self.config_path = kwargs.get("config_path", None)

    def get_factories(self):
        """Returns a dict of all factory objects corresponding to their appropriate method names
        
        Returns
        -------
        dict
        """
        factory_args = []
        for params in self.config_params:
            name = params["name"]
            config = params.get("config_dict", None)
            parser = ParseConfig(name, config, self.config_path)
            factory_args.append(parser.get_factory_dict())
        return merge_dicts(*factory_args)

    def build_factory_facade(self):
        """Builds out an isolated namespace containing all factory methods parsed from config
        
        Returns
        -------
        argparse.Namespace
        """
        kwargs = self.get_factories()
        instance = Namespace(**kwargs)
        return instance
