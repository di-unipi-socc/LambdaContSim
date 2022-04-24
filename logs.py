import logging

def get_logger():
    logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s')
    
    # Creating an object
    logger = logging.getLogger()
 
    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)
    
    return logger