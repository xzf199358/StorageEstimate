# -*- coding: UTF-8 -*-
# this module is to load configurations for DBAI

import os
import sys
import configparser
from version import program_version_no

class ConfigPara:
    database_host = 'localhost'
    database_port = '5432'
    database_name = 'postgres'
    database_user_name = 'postgres'
    database_password = '123456'
    generate_picking_call_interval = 9
    cart_prediction_update_interval = 10
    workload_balance_call_interval = 60
    update_all_cart_time_interval = 1
    update_ods_task_time_interval = 10.0
    reload_config_interval = 5
    max_connection_num = 6
    mincached_num = 5
    maxcached_num = 5
    maxshared_num = 5
    application_name_for_connections = 'DBAI'
    blocking = False
    logger_name = 'root'
    clear_agv_command_task_time_interval = 60

    @classmethod
    def load_DBconfig(cls):
        config_file_path = ''
        try:
            current_path = os.getcwd()
            config_file_path = current_path + "/config/DBconfig.ini"
            print('loading config file at path: ' + config_file_path)
            config_reader = configparser.ConfigParser()
            config_reader.read(config_file_path)
            cls.database_host = config_reader.get('database_connection', 'host')  # '127.0.0.1'
            cls.database_port = config_reader.get('database_connection', 'port')  # '5432'
            cls.database_name = config_reader.get('database_connection', 'database_name')  # 'hprpoc'
            cls.database_user_name = config_reader.get('database_connection', 'user_name')  # 'hpr_appl'
            cls.database_password = config_reader.get('database_connection', 'password')  # 'hpr#appl'
            return cls

        except Exception as e:
            print('Error: failed to read configuration file! File path should be at: ' + config_file_path1)
            print(e)
            sys.exit(1) # fatal error, need exit the program

    @classmethod
    def load_config(cls):
        config_file_path = ''
        try:
            current_path = os.getcwd()
            config_file_path = current_path + "/config/config.ini"
            print('loading config file at path: ' + config_file_path)
            config_reader = configparser.ConfigParser()
            config_reader.read(config_file_path)
            '''
            cls.database_host = config_reader.get('database_connection', 'host')  # '127.0.0.1'
            cls.database_port = config_reader.get('database_connection', 'port')  # '5432'
            cls.database_name = config_reader.get('database_connection', 'database_name')  # 'hprpoc'
            cls.database_user_name = config_reader.get('database_connection', 'user_name')  # 'hpr_appl'
            cls.database_password = config_reader.get('database_connection', 'password')  # 'hpr#appl'
            '''
            ConfigPara.load_DBconfig()
            cls.generate_picking_call_interval = config_reader.getfloat('generate_picking', 'call_interval') # unit: seconds

            cls.cart_prediction_update_interval = config_reader.getfloat('cart_prediction', 'update_interval')

            cls.workload_balance_call_interval = config_reader.getfloat('workload_balance', 'call_interval') # unit: seconds

            cls.update_all_cart_time_interval = config_reader.getfloat('update_all_cart','update_interval') # unit: seconds

            cls.clear_agv_command_task_time_interval = config_reader.getfloat('clear_agv_command_task','update_interval') # unit: seconds
            cls.aisle_station_distance_interval = config_reader.getfloat('update_aisle_station_distance','update_interval')  # unit: seconds
            cls.aisle_station_distance_sampling_time = config_reader.getfloat('update_aisle_station_distance', 'sampling_time')  # unit: day
            cls.aisle_station_distance_sample_slice = config_reader.getfloat('update_aisle_station_distance','sample_slice')  # unit: day

            cls.reload_config_interval = config_reader.getfloat('reload_config_from_database','update_interval') # unit: seconds

            cls.update_ods_task_time_interval = config_reader.getfloat('generate_ods_task','update_interval') # unit: seconds
            cls.max_connection_num = config_reader.getint('db_connection_pool', 'max_connection_num')
            cls.mincached_num = config_reader.getint('db_connection_pool', 'mincached_num')
            cls.maxcached_num = config_reader.getint('db_connection_pool', 'maxcached_num')
            cls.maxshared_num = config_reader.getint('db_connection_pool', 'maxshared_num')
            cls.application_name_for_connections = config_reader.get('db_connection_pool', 'application_name_for_connections')
            cls.application_name_for_connections = cls.application_name_for_connections + '_' + program_version_no
            blocking = config_reader.getint('db_connection_pool', 'blocking')

            if blocking is 0:
                cls.blocking = False
            else:
                cls.blocking = True

            cls.logger_name = config_reader.get('logger', 'logger_name')

            return cls

        except Exception as e:
            print('Error: failed to read configuration file! File path should be at: ' + config_file_path)
            print(e)
            sys.exit(1) # fatal error, need exit the program

configs =  ConfigPara.load_config()

class DatabaseConnectionConfig:
    def __init__(self, host, port, database_name, user_name, password):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user_name = user_name
        self.password = password


if __name__ == "__main__":
    print(configs.database_host)
    print(configs.database_port)
    print(configs.database_name)
    print(configs.database_password)
    print(configs.database_user_name)
    print(configs.mincached_num)









