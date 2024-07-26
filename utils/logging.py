import logging


def create_logger(module_name):
    """
    Initializes a new logger object.

    Args:
        module_name (str): Name of the module importing the logger.

    Returns:
        logging.Logger: Logger object configured with a stream handler and a file handler.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("qa.log", mode="a", encoding="utf-8")

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    return logger
