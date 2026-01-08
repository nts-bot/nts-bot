"""

Description: Main File
Authors: GAMM
Version: 2
Year: 2025-11-17

"""

# .1 Standard Libraries
import os
import git
import logging
import traceback

from py import jon
from py.utils import logger, rnw_json
from py.script import connection, nts
from py.main import scrape, runscript

# .2 Local Libraries
logger(False)  # Start Log


# .3 Init Class
connection.connect()  # Test Connection
class_instance = nts()

# .4 Main Logic
test = rnw_json(jon("config"))["Test"]


def check():
    try:
        up = rnw_json(jon("pid"))
    except:
        logging.info(".PID ERROR.")
        up = rnw_json(jon(["backup","pid"]))
        rnw_json(jon("pid"), up)


def main(self):
    shelf = scrape(test)
    runscript(self, test, list(shelf), retry=True)


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
        _git()
    except Exception as error:
        print("--------------\nCheck LOG file\n--------------")
        print(f"Error: '{error}'")
        logging.warning(traceback.format_exc())
