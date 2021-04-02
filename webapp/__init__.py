import logging

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_logger(name):
    """Настройка логирования."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    path_to_log_file = "debugging.log"
    date_time_format = "%d-%m-%Y %H:%M:%S"

    logging.basicConfig(filename=path_to_log_file,
                        format=log_format,
                        datefmt=date_time_format,
                        level=logging.INFO)

    return logging.getLogger(name)
