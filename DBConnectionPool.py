# -*- coding: UTF-8 -*-

from DBUtils.PooledDB import PooledDB
import ConfigManager
import psycopg2
from ConfigManager import configs
import sys


class DBConnectionPool:
    def __init__(self, configs):
        try:
            self.pool = PooledDB(psycopg2, maxconnections = configs.max_connection_num, mincached = configs.mincached_num, maxcached = configs.maxcached_num, \
                             maxshared = configs.maxshared_num, application_name = configs.application_name_for_connections,
                             host = configs.database_host,port=configs.database_port, dbname = configs.database_name, user = configs.database_user_name, password=configs.database_password)
        except Exception as e:
            logger.error("Fatal Error: failed to initialize DBConnectionPool, system is exiting!")
            logger.error(e)
            sys.exit(901)

    def get_connection(self):
        try:
            return self.pool.connection()
        except Exception as e:
            logger.error("Error: get connection from pool error!")
            logger.error(e)
        return None

    def get_dedicated_connection(self):
        try:
            return self.pool.dedicated_connection()
        except Exception as e:
            logger.error("Error: get dedicated connection from pool error!")
            logger.error(e)
        return None

pool = DBConnectionPool(configs)