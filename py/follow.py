"""

Description: Follow
Authors: GAMM
Version: 1
Year: 2023-09-02

"""

# .1 Standard Libraries
import sys
import logging
import traceback
from importlib import import_module

# .2 Local Libraries
sys.path.insert(0, "./py")
utils = import_module("utils")
utils.logger(True)  # Start Log

# .3 Init Class
script = import_module("script")
class_instance = script.nts()

# .4 Follow
try:
    class_instance.follow()
except:
    logging.warning(traceback.format_exc())
