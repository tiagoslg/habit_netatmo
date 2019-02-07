import logging


def get_log_file_name(user_id, device_id):
    return '/app/{}_{}.log'.format(user_id, device_id.replace(':', ''))


class Logger:
    def __init__(self, level, user_id, device_id, name=''):
        self.level = level
        self.user_id = user_id
        self.device_id = device_id
        self.name = __name__ if not name else name

    def my_logger(self):
        logger = logging.getLogger(self.name)

        # verify if this log has any handlers, and clear if found
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(self.level)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        # create a file handler
        handler = logging.FileHandler(get_log_file_name(self.user_id, self.device_id))
        handler.setLevel(self.level)
        handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)

        return logger