# -*- coding: utf-8 -*-

from builtins import super, str

import json
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from memoized import memoized

from .util import extend_docs
from .exceptions import ConfigurationException

from .config_util import full_path, parse_config


__all__ = [
    'SqlClient',
    'get_client_factory'
]


class SqlClient(Engine):
    """This is a convenience wrapper around :class:`sqlalchemy.engine.Engine`.
    Given a config_file and env, it reads the connection information from the
    configuration file and creates an ``Engine``; it sets up a
    :class:`sqlalchemy.engine.reflection.Inspector` that enables you to explore the
    data source; it sets up a :class:`sqlalchemy.schema.MetaData` to hold metadata
    about the tables; it sets up a wrapper to :any:`pandas.read_sql` using itself as a
    connection; and it sets up some convenience functions for working with
    :any:`sqlalchemy.orm.session.sessionmaker`.

    The preferred way to instanciate this is by using :any:`get_client_factory` in a
    a submodule for the specific data source. You can then create a
    :any:`get_client` function with the defaults for that data
    source. When :any:`get_client` is called, it'll maintain a singleton for each specific
    configuration.
    """
    @extend_docs(create_engine)
    def __init__(self, config_file, env='default', default_schema=None,
                 reflect=False, **kwargs):
        """Instanciate a :class:`SqlClient` with the given params.

        :param str config_file: Name of config file without the file extension
        :param str env: Name of the environment within the config file
             (Default value = 'default')
        :param str default_schema: Name of default schema, used by the
             :class:`sqlalchemy.schema.MetaData` instance and by :any:`get_table`
             (Default value = None)
        :param bool reflect: Whether to try to reflect the
             :class:`sqlalchemy.schema.MetaData` (Default value = False)

        See :any:`sqlalchemy.create_engine` for ``**kwargs``:
        """
        #: Name of config file without file extension
        self.config_file = config_file

        #: Name of environment within the config file
        self.env = env

        engine = create_engine(self._get_url(), **kwargs)
        self.__dict__.update(engine.__dict__)

        # wrap in try catch because jdv fails to initialize
        try:
            # no-op connection to initialize engine, inspector, etc
            with self.begin():
                pass
        except:
            pass

        #: Instance of :class:`sqlalchemy.engine.reflection.Inspector` using ``self``
        #: as bind. Useful for exploring what's available in the data source
        self.inspector = inspect(self)

        #: Instance of :class:`sqlalchemy.schema.MetaData` using ``self`` as bind.
        #: Useful for keeping table and view metadata
        self.metadata = MetaData(bind=self, schema=default_schema)
        if reflect:
            self.metadata.reflect(views=True)

        self.default_schema = default_schema

    def __repr__(self):
        return super().__repr__().replace('Engine', 'SqlClient')

    def __getitem__(self, key):
        """Return the given table"""
        if key in self.metadata.tables:
            return self.metadata.tables[key]
        else:
            return self.get_table(key)

    def _get_url(self):
        """Returns a SQLAlchemy URL from given env"""
        path = full_path(str(self.config_file) + '.json')

        try:
            with open(path) as reader:
                conf = json.load(reader)

                return parse_config(conf, self.env)
        except IOError:
            raise ConfigurationException('Config file not found')

    @property
    def default_schema(self):
        """The default schema for this connection. It is useful for :any:`get_table` and
        for :any:`metadata`
        """
        return self._default_schema

    @default_schema.setter
    def default_schema(self, schema):
        """Set default schema

        :param str schema: Name of schema to use as default

        """
        self._default_schema = schema
        self.metadata.schema = schema

    def reflect_schema(self, schema):
        """Automatically fetch all metadata related to the given schema

        :param str schema: Name of schema to pull down

        """
        self.metadata.reflect(schema=schema, views=True)

    def get_table(self, name, schema=None):
        """Fetch metadata for the given table name. This will add it to the current
        metadata and save it for later use.

        :param str name: Name of the table, can include schema name with dot notation
        :param str schema: Explicitly give schema name (Default value = None)

        """
        name, schema = _parse_table_name(name, schema or self.default_schema)
        return Table(name, self.metadata, autoload=True, schema=schema)

    def table_factory(self, name, schema=None, primarykey=None):
        """Create a table using :any:`sqlalchemy.ext.declarative`. This would generaly
        be used for ORM like operations. Usually, :any:`get_table` will be
        enough.

        :param str name: Name of the table, can include schema name with dot notation
        :param str schema: Explicitly give schema name (Default value = None)
        :param str primarykey: Column name for primary key (Default value = None)

        """
        tbl = self.get_table(name, schema=schema)
        bases = (declarative_base(),)
        attrs = {'__table__': tbl,
                 '__mapper_args__': {}}
        if primarykey:
            attrs['__mapper_args__']['primary_key'] = [
                getattr(tbl.c, x) for x in primarykey
            ]
        return type(name, bases, attrs)

    @extend_docs(pd.read_sql, True)
    def read_sql(self, sql, **kwargs):
        """This is a wrapper around :any:`pandas.read_sql` using the current ``Engine``
        as con.

        Docstring for :any:`pandas.read_sql`:
        """
        return pd.read_sql(sql, con=self, **kwargs)

    @extend_docs(sessionmaker)
    def create_session(self, **kwargs):
        """This is a wrapper around :any:`sqlalchemy.orm.session.sessionmaker` using
        current ``Engine`` as bind.

        Docstring for :any:`sqlalchemy.orm.session.sessionmaker`:
        """
        return sessionmaker(bind=self, **kwargs)()

    @contextmanager
    @extend_docs(sessionmaker)
    def read_session(self, **kwargs):
        """This is a wrapper around :any:`sqlalchemy.orm.session.sessionmaker` using
        current ``Engine`` as bind and used as a contextmanager.

        For example::

            with SqlClientInstance.read_session() as sess:
                ... do things with session

        Docstring for :any:`sqlalchemy.orm.session.sessionmaker`:
        """
        session = self.create_session(**kwargs)
        try:
            yield session
        finally:
            session.close()


def _parse_table_name(table_name, schema=None):
    """Convenience to split a table name into schema and table or use the given
    schema. If a schema is passed it, it'll use that. Otherwise it'll try to parse
    it from the given name. For example 'schema.table_name' would be parsed into
    (table_name, schema)

    Returns a tuple (name, schema)

    :param str table_name: Name of the table, can include schema name with dot notation
    :param str schema: Explicitly give schema name (Default value = None)
    """
    parts = table_name.split('.')
    return (
        parts[-1],  # name
        schema or parts[0] if len(parts) == 2 else None  # schema
    )


def get_client_factory(config_file, default_env='default', default_schema=None,
                       default_reflect=False):
    """Wrapper function to create a :any:`get_client` function using the given
    ``config_file`` and setting the given defaults. This should be used in the submodule
    for each data source.

    :param str config_file: Name of config file without the extension
    :param str default_env: Set default environment to use (Default value = 'default')
    :param str default_schema: Set default schema to use  (Default value = None)
    :param bool default_reflect: Set default for reflect  (Default value = False)
    """
    @extend_docs(SqlClient.__init__)
    def get_client(env=default_env, default_schema=default_schema,
                   reflect=default_reflect, **kwargs):
        """Get a :any:`SqlClient` for the specified
        environment. Defaults are based on what was passed to :any:`get_client_factory`.

        See :any:`SqlClient.__init__` for params:
        """
        return SqlClient(config_file, env, default_schema, reflect, **kwargs)

    return memoized(get_client, signature_preserving=True)
