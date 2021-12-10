import logging


class Logger:
    def __init__(self, path, stream = True, output = True, slevel = logging.INFO, olevel = logging.DEBUG):
        self.logger = logging.getLogger(path)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        if stream:
            # 设置CMD日志
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
            sh.setLevel(slevel)
            self.logger.addHandler(sh)
        if output:
            # 设置文件日志
            fh = logging.FileHandler(path)
            fh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [file: %(filename)s] [func: %(funcName)s] [line: %(lineno)d] %(message)s', '%Y-%m-%d %H:%M:%S'))
            fh.setLevel(olevel)
            self.logger.addHandler(fh)

    def __del__(self):
        pass

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def war(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
