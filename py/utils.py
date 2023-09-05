"""

Description: Utils
Authors: GAMM
Version: 1
Year: 2023-09-02

"""

# .1 Standard Libraries
import os
import json
import time
import logging
import inspect
import functools
import traceback
import datetime as dt
from pprint import pformat
from threading import Thread
from timeit import default_timer as timer

"""

 0  - Debugging

"""


def monitor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        retval = func(*args, **kwargs)
        logging.debug(
            f"{func.__module__}.{func.__qualname__}"
            + "\n>>    "
            + pformat(f"({func_args_str})")
            + "\n->"
            + "\n>>    "
            + pformat(repr(retval))
            + "\n>>    "
            + f"{round(timer() - start, 4)} seconds."
        )
        return retval

    return wrapper


def logger(test):
    _ = f"{os.getcwd()}/py/.log"
    if not os.path.exists(_):
        os.makedirs(_)
    name = f"{dt.datetime.now().strftime('%Y%m%d-%H%M')}_{os.getlogin()}.log"

    rootlogger = logging.getLogger()

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    fileHandler = logging.FileHandler(f"{_}/{name}")
    fileHandler.setFormatter(logFormatter)

    if test:
        rootlogger.setLevel(logging.DEBUG)
    else:
        rootlogger.setLevel(logging.INFO)

    rootlogger.addHandler(fileHandler)
    return rootlogger


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [
                Exception(
                    "function [%s] timeout [%s seconds] exceeded!"
                    % (func.__name__, timeout)
                )
            ]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                logging.info("error starting thread")
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco


"""

 1 - Aux

"""


def rnw_json(filename, store=None):
    if store is None:
        logging.info(f"Opening: {filename}.json")
        try:
            with open(f"{filename}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.info(f"Creating: {filename}.json")
            rnw_json(filename, dict())
            return dict()
        except PermissionError:
            logging.info(f"Issues Accessing: {filename}.json")
            time.sleep(0.5)
            return rnw_json(filename)
        except Exception as error:
            logging.warning(traceback.format_exc())
            raise Exception(error)
    else:
        logging.info(f"Saving: {filename}.json")
        try:
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(store, f, ensure_ascii=False, sort_keys=True, indent=4)
        except:
            logging.warning(traceback.format_exc())
            time.sleep(0.5)
            rnw_json(filename, store)
