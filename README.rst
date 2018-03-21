==============
SQL Connectors
==============


.. image:: https://img.shields.io/pypi/v/sql_connectors.svg
        :target: https://pypi.python.org/pypi/sql_connectors

.. image:: https://img.shields.io/travis/aiguofer/sql_connectors.svg
        :target: https://travis-ci.org/aiguofer/sql_connectors

.. image:: https://readthedocs.org/projects/sql-connectors/badge/?version=latest
        :target: https://sql-connectors.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/aiguofer/sql_connectors/shield.svg
     :target: https://pyup.io/repos/github/aiguofer/sql_connectors/
     :alt: Updates



A simple wrapper for SQL connections using SQLAlchemy and Pandas read_sql to standardize SQL workflow. The main goals of this project is to reduce boilerplate code when working with SQL based data sources and to enable interactive exploration of data sources in Python.


* Free software: MIT license
* Documentation: https://sql-connectors.readthedocs.io.


Features
--------

* Standardized client for working with different SQL datasources, including a standardized format for defining your connection configurations
* A SqlClient interface based off the SQLAlchemy ``Engine`` with some helpful functions like Pandas' ``read_sql`` and functions to leverage ``reflection`` from SQLAlchemy

Configurations
--------------

You'll need to set your configuration files in ``~/.config/sql_connectors``. Optionally, you can specify a different configuration directory with the ``SQL_CONNECTORS_CONFIG_DIR`` environment variable. The ``example_connection.json`` file is provided as a template; feel free to replace this with your own connection details and re-name the file.

.. include:: example_connection.json
   :literal:

The fields mean the following:

   drivername (string)
      Required. This is a SQLAlchemy dialect or dialect+driver. See the `SQLAlchemy Engine documentation <http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_ for more details. You may first have to install the required python modules for your dialect+driver to work if it's a third party plug-in.

   relative_paths (list of strings)
      Optional. This field lets you specify if an option for your connection needs to load a file relative to your config directory. In the example above, it will convert ``certs/postgresql/root.crt`` to a full path using the config dir as the base.

   default_env (string)
      Optional. This field lets you specify which environment should be used by default. If not included, it will use ``default``.

   default_schema (string)
      Optional. This field lets you specify which schema should be used by default. If not included, it will use ``None``.

   default_reflect (boolean)
      Optional. This field lets you specify whether it should reflect the data source by default. If not included, it will use ``False``.

   env.username (string)
      Required. This field specifies the username for the connection.

   env.password (string)
      Required. This field specifies the password for the connection.

   env.host (string)
      Required. This field specifies the host for the connection.

   env.port (string or integer)
      Required. This field specifies the port for the connection.

   env.database (string)
      Required. This field specifies the database name for the connection.

   env.query (object)
      Optional. This field is a json object with options to pass onto the dialect and/or DBAPI upon connect.

How-To
------

The module will check your available connection configurations and create variables within the top level module for each of them. It will create 2 variables for each config, ``connection_name`` and ``connection_name_envs``; these are both functions, the first will return a ``get_client`` function with some defaults set based on the config, and the second will return a ``get_available_envs`` function that when called returns available environments for the given data source. When ``reflection`` is enabled, the client will hold metadata about the available tables.

Here's a basic usage example assuming the example config file exists:

.. code:: python

   from sql_connectors import example_connection, example_connection_vars

   available_envs = example_connection_vars()
   client = example_connection(env=available_envs[0], reflect=True)

   available_tables = client.table_names()
   table1 = client.get_table(available_tables[0])
   df = client.read_sql(table1.select())


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
