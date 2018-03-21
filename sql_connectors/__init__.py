# -*- coding: utf-8 -*-

from .config_util import get_available_envs_factory, get_available_configs
from .client import get_client_factory

configs = get_available_configs()

__all__ = [config for config, default in configs] + \
          [config + '_envs' for config, default in configs]

for config_file, defaults in configs:
    varname = config_file
    val = 'get_client_factory("{0}", "{1}", "{2}")'.format(config_file,
                                                           defaults['default_env'],
                                                           defaults['default_schema'])
    exec('{0}={1}'.format(varname, val))

    varname = config_file + '_envs'
    val = 'get_available_envs_factory("{0}")'.format(config_file)
    exec('{0}={1}'.format(varname, val))


# Delete temp variables so they don't pollute auto-complete
del configs
del config
del default
del config_file
del defaults
del get_available_envs_factory
del get_available_configs
del get_client_factory
del varname
del val
