import logging


def init_logger():

    # format the logging message
    # TIME - LOG LEVEL : message to print
    logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s")

    # Creating an object
    logger = logging.getLogger()

    # Setting the threshold of logger to INFO
    logger.setLevel(logging.INFO)

    return logger


def get_logger():
    return logging.getLogger()
