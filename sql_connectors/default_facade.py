from glob import glob
from .facade_builder import BuildFacade, full_path

def get_fname(fpath):
    """Gets filename without extension from full path
    
    Parameters
    ----------
    fpath : str
        full path
    
    Returns
    -------
    str
    """
    return fpath.split("/")[-1].replace(".json", "")


def get_default_params(config_path=None):
    """Gets default params from a config location on disk
    
    Parameters
    ----------
    config_path : str, optional
        config location on disk - defaults to the SQL_CONNECTORS_CONFIG_DIR environment var
    
    Returns
    -------
    tuple of dicts
        iterable of config file names to pass into `BuildFacade`
    """
    configs = glob(full_path("*json", config_dir = config_path))
    names = [get_fname(i) for i in configs]
    return tuple({"name": name} for name in names)


def default_facade(**kwargs):
    """Function to build out the connector facade from the default config path

    Parameters
    ----------
    **kwargs
    config_path: str
        location of config file - defaults to the SQL_CONNECTORS_CONFIG_DIR environment var

    Returns
    -------
    argparse.Namespace
    """
    config_path = kwargs.get("config_path", None)
    params = get_default_params(config_path)
    cls = BuildFacade(params)
    return cls.build_factory_facade()

DefaultFacade = default_facade()