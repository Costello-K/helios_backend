import os
import logging
from django.conf import settings


# path to the log folder
log_dir = os.path.join(settings.BASE_DIR, 'logs')

# create a folder for logs if it does not exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# log file storage path
log_file = os.path.join(log_dir, 'event_log.log')

# create a logger instance
logger = logging.getLogger(__name__)
# set the logging level for the logger to INFO
logger.setLevel(logging.INFO)

# set the log format
formatter = logging.Formatter('%(asctime)-25s %(filename)-20s %(lineno)-3d %(levelname)-8s %(message)s')

# create a file handler for logging, specifying the log file path
filehandler = logging.FileHandler(log_file)
# set the logging level for the file handler to INFO
filehandler.setLevel(logging.INFO)
# apply the defined log message format to the file handler
filehandler.setFormatter(formatter)

# add a listener to the logger
logger.addHandler(filehandler)
