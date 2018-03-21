# -*- coding: utf-8 -*-

class SQLConnectorException(Exception):
    """Exception from SQL Connector"""

class ConfigurationException(SQLConnectorException):
    """Exception while reading the configuration"""
