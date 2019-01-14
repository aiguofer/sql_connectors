=======
History
=======

1.0.0 (2019-01-14)
------------------

* BREAKING: Connections are now stored in a namespace instead of being submodules.
  New usage:

  .. code-block:: python

     from sql_connectors import connections
     client = connections.example_connection()

  Instead of:

  .. code-block:: python

     from sql_connectors import example_connection
     client = example_connection()

* New ``Storage`` abstract class can be extended to implement different backend

* Configuration is now handled by ``Traitlets``. Default storage class can be specified
  with ``SQL_CONNECTORS_STORAGE`` env var and the connection string or path can be
  specified with ``SQL_CONNECTORS_PATH_OR_URI``

0.1.0 (2018-03-20)
------------------

* First release on PyPI.
