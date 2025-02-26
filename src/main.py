from constants import logging, O_SETG
from api import Helper
from strategies.strategy import Strategy
from toolkit.kokoo import is_time_past, kill_tmux
from traceback import print_exc


def wait_until_start(start):
    is_start = is_time_past(start)
    while not is_start:
        print(f"waiting for {start}")
    else:
        logging.info("program started")


def intiialize():
    Helper.api()


def main():
    try:
        start = O_SETG["program"].pop("start")
        wait_until_start(start)
        intiialize()
        obj = Strategy(**O_SETG)
        stop = O_SETG["trade"]["stop"]

        while not is_time_past(stop):
            obj.run(Helper.orders())
        else:
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


main()
