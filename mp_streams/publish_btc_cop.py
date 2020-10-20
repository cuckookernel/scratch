"""Publish btc cop every 10 minutes as given by
https://www.buda.com/api/v2/markets/btc-cop/ticker
"""

import os
import sys
import json
import logging as log

from microprediction.polling import MicroPoll
import requests

# log.basicConfig(filename='publish_btc_cop.log', level=log.INFO)
log.basicConfig(stream=sys.stderr, level=log.INFO)
log.info('Publishing starts')


class _Config:
    keys_file = os.getenv('HOME') + '/keys.json'
    stream_name = 'cck-btc-cop.json'
    ticker_url = 'https://www.buda.com/api/v2/markets/btc-cop/ticker'
    interval = 10  # minutes
    key_server_url = 'https://localhost:8000/key?client_name=cck-btc-cop'


CFG = _Config

# %%


class MicroPollV2( MicroPoll ):
    """Version of Micropoll that fetches keys from a key server"""

    def maybe_bolster_balance_by_mining(self):
        balance = self.get_balance()
        log.info(f'at the start, balance: {balance}')

        if balance < 0:
            response_js = requests.get(CFG.key_server_url).json()
            key = response_js['key']
            difficulty = response_js['difficulty']
            print(f"Got key of difficulty {difficulty} from server")
            self.put_balance(source_write_key=key)
            balance = self.get_balance()
            log.info(f'at the end, balance: {balance}')


def main():
    """get key, instantiate feed, run it"""

    write_key = _get_key( CFG.stream_name, CFG.keys_file )
    assert write_key, f"Failed getting key for `{CFG.stream_name}` from file: {CFG.keys_file}"

    feed = MicroPollV2( name=CFG.stream_name,
                        write_key=write_key,
                        func=get_price,
                        interval=CFG.interval)

    feed.run()


def get_price():
    """Query ticker url return last price"""
    last_price = None
    try:
        response = requests.get(CFG.ticker_url)
        last_price = float( response.json()['ticker']['last_price'][0] )
    except Exception as exc:
        log.warning( f"Exception getting ticker:\n{exc}\n{response.json()}\n"
                     f"last_price={last_price}" )

    return last_price


def _get_key( stream_name: str, keys_file: str) -> str:
    with open( keys_file ) as f_in:
        obj = json.load(f_in)
        return obj[stream_name]


if __name__ == "__main__":
    main()
