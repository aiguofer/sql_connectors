# -*- coding: utf-8 -*-
from .config_util import get_available_envs_factory, get_available_configs
from .client import get_client_factory
from ._version import __version__, __version_info__

def setup():
    """Create get_client and get_available_envs functions for each datasource using
    the datasource name as the variable names. It also adds them to __all__ so they
    show up in auto-complete when importing"""
    global __all__

    configs = get_available_configs()

    __all__ = [config for config, default in configs] + \
              [config + '_envs' for config, default in configs]

    for config_file, defaults in configs:
        varname = config_file
        schema = defaults['default_schema']

        val = """get_client_factory("{0}", "{1}", {2}, {3})
        """.format(config_file,
                   defaults['default_env'],
                   '"{0}"'.format(schema) if schema is not None else schema,
                   defaults['default_reflect'])
        exec('{0}={1}'.format(varname, val), globals())

        varname = config_file + '_envs'
        val = 'get_available_envs_factory("{0}")'.format(config_file)
        exec('{0}={1}'.format(varname, val), globals())

def teardown():
    # Delete temp variables so they don't pollute auto-complete in ipython
    # this is only useful in python 2.7, doesn't seem to matter in python 3
    for var in ['get_available_envs_factory', 'get_available_configs',
                'get_client_factory', 'setup', 'teardown']:
        if var in globals():
            del globals()[var]


setup()
teardown()
