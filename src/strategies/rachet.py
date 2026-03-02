
from re import S
from toolkit.kokoo import is_time_past
from src.constants import logging_func, S_DATA


import csv
import pendulum as pdlm
logging = logging_func(__name__)


def history_to_csv(data_list):
# Your data list (assuming it is named 'data_list')
# fieldnames should match the keys in your dictionary
    fieldnames = ['date', 'open', 'high', 'low', 'close', 'volume']

    with open(S_DATA + 'market_data.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data_list:
            
            # Convert the datetime object to a Pendulum instance and format it
            # 'YYYY-MM-DD' for date only, or 'YYYY-MM-DD HH:mm:ss' for full timestamp
            row['date'] = pdlm.instance(row['date']).format('YYYY-MM-DD')
            
            writer.writerow(row)

class Rachet:
    def __init__(self, **O_SETG):
        self.strategy = O_SETG["strategy"]
        self._removable = False
        self._tradingsymbol = O_SETG["tradingsymbol"]
        self._token = O_SETG["instrument_token"]
        self.stop_time = O_SETG["stop_time"]
        self._rest = O_SETG["rest"]
        resp = self._rest.weekly(self._token)
        history_to_csv(resp)
        self._fn = "is_entry"
        print(O_SETG)

    def is_entry(self):
        print("is entry")

    def remove_me(self):
        print("remove me")

    def run(self, trades, quotes, positions):
        print("running")
        if is_time_past(self.stop_time):
            self.remove_me()
            logging.info(
                f"REMOVING: {self._tradingsymbol} switching from waiting for breakout"
            )
            return

        return getattr(self, self._fn)()
