"""
Tuấn Anh, nt.anh.fai@gmail.com
Create Date: $
Create Time: $
"""
import logging
import logging
import os
from datetime import datetime
from os.path import basename


class MyLogger:
    def __init__(self, name="__App_data/log/mday/program.log", level=logging.DEBUG):
        name = name.replace('mday', datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(basename(name), exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.handler = logging.StreamHandler()
        self.handler.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)


if __name__ == '__main__':
    pass
