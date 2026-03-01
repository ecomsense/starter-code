from traceback import print_exc

import pendulum as pdlm
from src.constants import yml_to_obj, S_DATA
from toolkit.fileutils import Fileutils
from toolkit.kokoo import blink



def get_bypass(O_CNFG):
    from stock_brokers.bypass.bypass import Bypass

    try:

        if isinstance(O_CNFG, dict):
            dct = O_CNFG["bypass"]

            tokpath = S_DATA + dct["userid"] + ".txt"
            enctoken = None
            if not Fileutils().is_file_not_2day(tokpath):
                print(f"{tokpath} modified today ... reading {enctoken}")
                with open(tokpath, "r") as tf:
                    enctoken = tf.read()
                    if len(enctoken) < 5:
                        enctoken = None
            print(f"enctoken to broker {enctoken}")
            bypass = Bypass(
                dct["userid"], dct["password"], dct["totp"], tokpath, enctoken
            )
            if bypass.authenticate():
                if not enctoken:
                    enctoken = bypass.kite.enctoken
                    with open(tokpath, "w") as tw:
                        tw.write(enctoken)
            else:
                raise Exception("unable to authenticate")
    except Exception as e:
        print(f"unable to create bypass object {e}")
        remove_token(tokpath)
        # get_bypass()
        print_exc()
    else:
        return bypass


def get_zerodha(O_CNFG):
    try:
        from stock_brokers.zerodha.zerodha import Zerodha

        zera = None
        if isinstance(O_CNFG, dict):
            dct = O_CNFG["zerodha"]
            # tokpath = S_DATA + dct["userid"] + ".txt"
            zera = Zerodha(
                userid=dct["userid"],
                password=dct["password"],
                totp=dct["totp"],
                api_key=dct["api_key"],
                secret=dct["secret"],
            )
            if not zera.authenticate():
                raise Exception("unable to authenticate")

    except Exception as e:
        print(f"exception while creating zerodha object {e}")
        # remove_token(tokpath)
        get_zerodha(O_CNFG)
    else:
        return zera


def remove_token(tokpath):
    __import__("os").remove(tokpath)


def login():
    O_CNFG = yml_to_obj()
    if isinstance(O_CNFG, dict):
        if O_CNFG["broker"] == "bypass":
            return get_bypass(O_CNFG)
        else:
            return get_zerodha(O_CNFG)
    else:
        print(f"please configure {O_CNFG} the settings properly")

class Helper:
    _api = None

    @classmethod
    def api(cls):
        if cls._api is None:
            cls._api = login()
            cls._rest = RestApi(cls._api)
            #ws = Wserver(cls._api, ["NSE:24"])
            cls._quote = QuoteApi(ws=None)
        cls.wait_till = pdlm.now().add(seconds=1)
        return cls._api

class RestApi:

    baseline = {}

    def __init__(self, session):
        self._api = session


    @classmethod
    def _get_history(cls, instrument_token):
        try:
            broker_object = cls.api()
            kwargs = dict(
                instrument_token=instrument_token,
                from_date=pdlm.now("Asia/Kolkata").subtract(days=6).to_date_string(),
                to_date=pdlm.now("Asia/Kolkata").to_date_string(),
                interval="day",
            )
            lst = broker_object.historical(kwargs)
            if isinstance(lst, list) and len(lst) > 0:
                cls.baseline[instrument_token] = lst[-1].get("close", 0)
                return cls.baseline[instrument_token]
            return 0
        except Exception as e:
            print(f"{e} exception while getting history")

    @classmethod
    def history(cls, instrument_token):
        return cls.baseline.get(instrument_token, cls._get_history(instrument_token))




class QuoteApi:
    subscribed = {}

    def __init__(self, ws):
        self._ws = ws

    def get_quotes(self):
        try:
            quote = {}
            ltps = self._ws.ltp
            quote = {
                symbol: ltps.get(values["key"])
                for symbol, values in self.subscribed.items()
            }
        except Exception as e:
            logging.error(f"{e} while getting quote")
            print_exc()
        finally:
            return quote

    def _subscribe_till_ltp(self, ws_key):
        try:
            quotes = self._ws.ltp
            ltp = quotes.get(ws_key, None)
            while ltp is None:
                self._ws.subscribe([ws_key])
                quotes = self._ws.ltp
                ltp = quotes.get(ws_key, None)
                print(f"trying to get quote for {ws_key} {ltp}")
                blink()
        except Exception as e:
            logging.error(f"{e} while get ltp")
            print_exc()

    def symbol_info(self, exchange, symbol, token=None):
        try:
            if self.subscribed.get(symbol, None) is None:
                if token is None:
                    logging.info(f"Helper: getting token for {exchange} {symbol}")
                    token = str(self._ws.api.instrument_symbol(exchange, symbol))
                key = exchange + "|" + str(token)
                self.subscribed[symbol] = {
                    "symbol": symbol,
                    "key": key,
                    "token": token,
                    "ltp": self._subscribe_till_ltp(key),
                }
            if self.subscribed.get(symbol, None) is not None:
                quotes = self._ws.ltp
                ws_key = self.subscribed[symbol]["key"]
                self.subscribed[symbol]["ltp"] = float(quotes[ws_key])
                return self.subscribed[symbol]
        except Exception as e:
            logging.error(f"{e} while symbol info")
            print_exc()



if __name__ == "__main__":
    resp = Helper.history(15420930)
    print(resp)
