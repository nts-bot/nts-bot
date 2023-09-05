"""

Description: Main File
Authors: GAMM
Version: 1
Year: 2023-09-02

"""

# .1 Standard Libraries
import os
import git
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

# .4 Main Logic
main_logic = import_module("main")
test = utils.rnw_json("config")["Test"]


def check():
    try:
        up = script.utils.rnw_json("./pid")
    except:
        logging.info(".PID ERROR.")
        up = script.utils.rnw_json("./backup/pid")
        script.utils.rnw_json("./pid", up)


def main(self):
    shelf = main_logic.scrape(test)
    main_logic.runscript(self, test, list(shelf), retry=True)


def _git():
    repo = git.Repo(os.getenv("directory"))
    repo.git.add(".")  # update=True
    repo.index.commit("auto-gitpush")
    origin = repo.remote(name="origin")
    origin.push()


if __name__ == "__main__":
    try:
        check()
        main(class_instance)
        import_module("count")
        _git()
    except Exception as error:
        print("--------------\nCheck LOG file\n--------------")
        print(f"Error: '{error}'")
        logging.warning(traceback.format_exc())
