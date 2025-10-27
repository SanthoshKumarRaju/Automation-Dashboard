import logging
import os
import gzip
from logging.handlers import RotatingFileHandler
from app.configurations.config import Settings

settings = Settings()

# Log level can be any of the following:
# CRITICAL, FATAL, ERROR, WARN, WARNING, INFO, DEBUG, NOTSET
loglevel = settings.log_level

# Logging settings log name, max bytes, backup count
logfilename = settings.log_file
logfilemaxbytes = settings.log_file_max_bytes  
logfilebackupcount = settings.log_file_bac_count 


def file_namer(name):
    # Appends '.gz' extension to RotatingFileHandler's auto-generated file name.
    return name + ".gz"


def file_rotator(source, dest):
    """
    Compresses the log file using gzip (src) and moves it to a new destination (dest).
    Refer: https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
    """
    with open(source, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            f_out.writelines(f_in)
    os.remove(source)


def get_logger(name=__name__, log_filename=logfilename):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(loglevel)

    formatter = logging.Formatter("{asctime} - {levelname:<8} - [{module:^20}] - {message}", style='{', datefmt="%Y-%m-%d %H:%M:%S")

    if not os.path.exists('./logs'):
        os.makedirs('./logs')

    handler = RotatingFileHandler(
        filename=f'./logs/{log_filename}',
        mode='a',
        maxBytes=logfilemaxbytes,  # 10MB
        backupCount=logfilebackupcount # keep 20 backups
    )
    handler.rotator = file_rotator
    handler.namer = file_namer

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def suppress_logs():
    """
    Suppress all logs of level FATAL and below.
    Since the log level is set to FATAL, all logs will be suppressed.
    Severity Levels: CRITICAL = FATAL > ERROR > WARNING > INFO > DEBUG > NOTSET
    """
    logging.disable(logging.FATAL)
