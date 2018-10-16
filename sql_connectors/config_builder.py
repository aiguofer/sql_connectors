from builtins import super
from argparse import Namespace


class ParseJSON(object):
    def __init__(self, **kwargs):
        return

    def parse(self, **kwargs):
        return


class ParseConfig(ParseJSON):
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
