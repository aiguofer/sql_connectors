from .config_util import get_available_envs_factory as _envs_factory, get_available_configs as _get_available_configs
from .client import get_client_factory as _client_factory

_configs = _get_available_configs()

__all__ = [config for config, default in _configs] + \
          [config + '_envs' for config, default in _configs]

for config_file, defaults in _configs:
    exec('{0}={1}'.format(config_file,
                          '_client_factory("{0}", "{1}", "{2}")'.format(config_file,
                                                                        defaults['default_env'],
                                                                        defaults['default_schema'])))
    exec('{0}_envs={1}'.format(config_file, '_envs_factory("{0}")'.format(config_file)))
