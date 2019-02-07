import logging
import os
from enum import Enum


class LogTypes(Enum):
    CAMERA_CON_STATUS = 'camera_con_status'
    CAMERA_MON_STATUS = 'camera_mon_status'
    CAMERA_SD_CARD = 'camera_sd_card'

    def __str__(self):
        return str(self.value)


def get_log_file_name(user_id, device_id, type_log=''):
    dest = '/app/media/{}/'.format(user_id)
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    return '{}{}_{}.log'.format(dest, type_log, device_id.replace(':', ''))


class Logger:
    def __init__(self, level, user_id, device_id, name='', type_log=''):
        self.level = level
        self.user_id = user_id
        self.device_id = device_id
        self.name = __name__ if not name else name
        self.type_log = type_log

    def my_logger(self):
        logger = logging.getLogger(self.name)

        # verify if this log has any handlers, and clear if found
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(self.level)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        # create a file handler
        handler = logging.FileHandler(get_log_file_name(self.user_id, self.device_id, self.type_log))
        handler.setLevel(self.level)
        handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)

        return logger