import logging
import logging.handlers


def setup_logger():
    log_format = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s \
        - %(message)s"
    date_format = "%d-%m %H:%M:%S"

    # Create a formatter with the desired format
    formatter = logging.Formatter(log_format, date_format)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logging level you need

    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    return logger


# Initialize the logger when the module is imported
logger = setup_logger()
