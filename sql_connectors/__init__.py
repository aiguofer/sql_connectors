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


# Delete temp variables so they don't pollute auto-complete in ipython
# this is only useful in python 2.7, doesn't seem to matter in python 3
for var in ['configs', 'config', 'default', 'config_file', 'defaults',
            'get_available_envs_factory', 'get_available_configs',
            'get_client_factory', 'varname', 'val', 'var']:
    if var in locals():
        del locals()[var]
