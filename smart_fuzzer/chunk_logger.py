import logging

class Logger:
    def __init__(self, name):
        self.name = name
    
    def log(self, message):
        logger = logging.getLogger(self.name)
        logger.debug(message)