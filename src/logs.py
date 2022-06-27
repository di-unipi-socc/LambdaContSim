import logging


def init_logger():
    """Init logger with error level"""

    # format the logging message
    # TIME - LOG LEVEL : message to print
    logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s")

    # Creating an object
    logger = logging.getLogger()

    # Setting the threshold of logger to ERROR
    logger.setLevel(logging.ERROR)

    return logger


def get_logger():
    return logging.getLogger()
