"""

Description: Weekly Tasks
Authors: GAMM
Version: 2
Year: 2023-09-18

"""

# .1 Standard Libraries
import sys
import logging
import traceback
from importlib import import_module

# .2 Local Libraries
sys.path.insert(0, "./py")
utils = import_module("utils")
utils.logger(False)  # Start Log

# .3 Init Class
script = import_module("script")
class_instance = script.nts()

# .4 todo
todo = ["counter", "privatise", "publicise", "follow"]

for i in todo:
    script.connection.connect()
    logging.info(f"Starting: {i}")
    try:
        eval(f"class_instance.{i}()")
    except:
        logging.warning(traceback.format_exc())
