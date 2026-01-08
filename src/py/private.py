"""

Description: Monthly Tasks
Authors: GAMM
Version: 2
Year: 2025-11-17

"""

import logging
import traceback

from .utils import logger
from .script import nts, connection

logger(False)  # Start Log

# .3 Init Class
class_instance = nts()

# .4 todo
todo = ["publicise"]

for i in todo:
    connection.connect()
    logging.info(f"Starting: {i}")
    try:
        getattr(class_instance, i)()
    except:
        logging.warning(traceback.format_exc())
