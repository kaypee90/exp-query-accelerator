import logging


def create_logger(module_name):
    """
    Initializes a new logger object.

    Parameters:
        module_name (str): Name of the module importing the logger.

    Returns:
        logging.Logger: Logger object configured with a stream handler and a file handler.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # Customize date format as needed
    )
    log_handler = logging.StreamHandler()
    log_file_handler = logging.FileHandler("qa.log")
    logger = logging.getLogger(module_name)
    logger.addHandler(log_handler)
    logger.addHandler(log_file_handler)
    return logger