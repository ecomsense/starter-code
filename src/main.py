from constants import logging, O_SETG
from sdk.helper import Helper
from strategies.strategy import Strategy
from toolkit.kokoo import is_time_past, kill_tmux
from traceback import print_exc


def main():
    try:
        Helper.api
        logging.info("HAPPY TRADING")
        while not is_time_past(O_SETG["trade"]["stop"]):
            obj = Strategy(O_SETG)
            obj.run(Helper.orders)
        else:
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


main()
