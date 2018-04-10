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
* Repo: https://github.com/aiguofer/sql_connectors.


Features
--------

* Standardized client for working with different SQL datasources, including a standardized format for defining your connection configurations
* A SqlClient interface based off the SQLAlchemy ``Engine`` with some helpful functions like Pandas' ``read_sql`` and functions to leverage ``reflection`` from SQLAlchemy

Installation
------------

Stable release
~~~~~~~~~~~~~~

To install SQL Connectors, run this command in your terminal:

.. code-block:: console

    $ pip install --process-dependency-links sql_connectors

This is the preferred method to install SQL Connectors, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Dev install
~~~~~~~~~~~

The sources for SQL Connectors can be downloaded from the `Github repo`_.

You can clone the public repository and install in development mode:

.. code-block:: console

    $ git clone git://github.com/aiguofer/sql_connectors
    $ cd sql_connectors
    $ pip install --process-dependency-links -e .[dev]


Configurations
--------------

You'll need to set your configuration files in ``~/.config/sql_connectors``. Optionally, you can specify a different configuration directory with the ``SQL_CONNECTORS_CONFIG_DIR`` environment variable. The ``example_connection.json`` file is provided as a template; feel free to replace this with your own connection details and re-name the file.

The contents of the example file are:

.. code:: javascript

   {
       "drivername": "sqlite",
       "relative_paths": ["database"],
       "default_env": "default",
       "default": {
           "database": "example_connection.db"
       }
   }

The fields mean the following:

   drivername (string)
      This required field is a SQLAlchemy dialect or dialect+driver. See the `SQLAlchemy Engine documentation <http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_ for more details. You may first have to install the required python modules for your dialect+driver to work if it's a third party plug-in.

   relative_paths (list of strings)
      This optional field lets you specify if an option for your connection needs to load a file relative to your config directory. For example, if you had a connection that needed to use a cert, you could add ``query.sslrootcert`` to this list, set ``"query": { "sslmode": "verify-ca", "sslrootcert": "certs/root.crt"}``, and drop the cert in ``$SQL_CONNECTORS_CONFIG_DIR/certs/root.crt``.

   default_env (string)
      This optional field lets you specify which environment should be used by default. If not included, it will use ``default``.

   default_schema (string)
      This optional field lets you specify which schema should be used by default. If not included, it will use ``None``.

   default_reflect (boolean)
      This optional field lets you specify whether it should reflect the data source by default. If not included, it will use ``False``.

   env.username (string)
      This optional field specifies the username for the connection. If it's left out or set to null and the driver is not 'sqlite', the user will be prompte when they try to create the client. If the connection doesn't have credentials, set this to an empty string. Should not be set for 'sqlite'.

   env.password (string)
      This optional field specifies the password for the connection. If it's left out or set to null and the driver is not 'sqlite', the user will be prompte when they try to create the client. If the connection doesn't have credentials, set this to an empty string. Should not be set for 'sqlite'.

   env.host (string)
      This optional field specifies the host for the connection. Should not be set for 'sqlite'.

   env.port (string or integer)
      This optional field specifies the port for the connection. Should not be set for 'sqlite'.

   env.database (string)
      This optional field specifies the database name for the connection. If it's a 'sqlite' connection and left empty, it will use ``:memory:``. Otherwise, you can specify a relative path or an absolute path; if you want the file in your config directory, you can use the ``relative_paths`` property.

   env.query (object)
      This optional field is a json object with options to pass onto the dialect and/or DBAPI upon connect.

   env.allowed_hosts (list of strings)
      This optional field is a list of strings containing hostnames where the given credentials are accepted. If the hostname is not in the list, it will prompt the user for credentials. This was added due to some specific usecase where we share service credentials but they're only allowed on our common servers.

How-To
------

The module will check your available connection configurations and create variables within the top level module for each of them. It will create 2 variables for each config, ``connection_name`` and ``connection_name_envs``; these are both functions, the first will return a ``get_client`` function with some defaults set based on the config, and the second will return a ``get_available_envs`` function that when called returns available environments for the given data source. When ``reflection`` is enabled, the client will hold metadata about the available tables.

Here's a basic usage example assuming the example config file exists:

.. code:: python

   from sql_connectors import example_connection
   client = example_connection()
   client.read_sql('select 1')


Here's a more complex example that's pretty redundant but shows more functionality

.. code:: python

   from sql_connectors import example_connection, example_connection_envs

   available_envs = example_connection_envs()
   client = example_connection(env=available_envs[0], reflect=True)

   client.read_sql('select 1').to_sql('example_table', client, if_exists='replace')
   available_tables = client.table_names()
   table1 = client.get_table(available_tables[0])
   df = client.read_sql(table1.select())


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Github repo: https://github.com/aiguofer/sql_connectors
