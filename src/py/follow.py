"""

Description: Weekly Tasks
Authors: GAMM
Version: 3
Year: 2025-11-17

"""

import logging
import traceback

from .utils import logger
from .script import nts, connection
logger(False)  # Start Log

class_instance = nts()

todo = ["follow"]

for i in todo:
    connection.connect()
    logging.info(f"Starting: {i}")
    try:
        getattr(class_instance, i)()
    except:
        logging.warning(traceback.format_exc())
