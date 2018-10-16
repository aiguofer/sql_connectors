from builtins import super
from argparse import Namespace
from six import iteritems

from .config_util import get_available_envs_factory, get_available_configs
from .client import get_client_factory


def merge_dicts(*args):
    # should raise warning for duplicate keys
    res_dict = {}
    for d in args:
        for k,v in iteritems(d):
            res_dict[k] = v
    return res_dict

def parse_config_entry(config_entry):
    fname, defaults = config_entry
    env = defaults.gets("default_env", None)
    schema = defaults.get("default_schema", "default")
    reflect = defaults.get("default_reflect", False)

    client_factory = get_client_factory(env, schema, reflect)
    env_factory = get_available_envs_factory("fname")

    parsed_kwarg = {fname: client_factory,
                    fname+"_envs": env_factory}
    return parsed_kwarg


class ParseConfig(object):
    def __init__(self, **kwargs):
        return

    def _read_file(self):

        return

    def _read_redis(self):
        return

    def parse(self, method="file"):
        return


class BuildFacade(ParseConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build_config_kwargs(self):
        return

    def build_facade(self):
        kwargs = self.build_config_kwargs()
        instance = Namespace(**kwargs)
        return instance


def default_facade(**kwargs):
    cls = BuildFacade(**kwargs)
    return cls.build_facade()
