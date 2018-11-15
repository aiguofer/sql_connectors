def setup():
    from .config import Config

    default_config = Config()
    default_connections = default_config.backend_storage.connections

    globals().update(default_connections.__dict__)
    del globals()["setup"]


setup()
