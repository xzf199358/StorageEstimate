# -*- coding: UTF-8 -*-

import logging
import logging.config
from ConfigManager import configs
import os
import sys

class Logger:
    def __init__(self):
        try:
            current_path = os.getcwd()
            conf_file_path = os.path.join(current_path, 'config/logging_module.conf')
            logging.config.fileConfig(conf_file_path)
            self.logger = logging.getLogger(configs.logger_name)
        except Exception as e:
            print('Error: init logger')
            sys.exit(2)

    def get_logger(self):
        return self.logger

logger = Logger().get_logger()

