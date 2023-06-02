import os
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

KEY = os.getenv('FXTOKEN')
PAIR = 'USDJPY'
START = '2022-06-01'
END = datetime.now()
MODE = 'daily'
TIME0 = '2022-04-20-00:00'
TIME1 = datetime.now() - timedelta(minutes=1)
if END - datetime(year=int(START[:4]), month=int(START[5:7]), day=int(START[-2:])) >= timedelta(days=365):
    START = (END - timedelta(days=365)).strftime('%Y-%m-%d-%H:%M')
if TIME1 - datetime(year=int(TIME0[:4]), month=int(TIME0[5:7]), day=int(TIME0[8:10]), hour=int(TIME0[11:13]), minute=int(TIME0[-2:])) >= timedelta(days=30):
    TIME0 = (TIME1 - timedelta(days=29)).strftime('%Y-%m-%d-%H:%M')


class Pair:

    def __init__(self, pair: str = PAIR, start: str = START, time0: str = TIME0, time1: str = TIME1.strftime('%Y-%m-%d-%H:%M'), end: str = END.strftime('%Y-%m-%d-%H:%M'), mode: str = MODE, key: str = KEY) -> None:
        self.pair = pair
        self.mode = mode
        if mode == 'daily': self.ts = self.get_ts(pair, start, end, key, mode)
        elif mode == 'hourly': self.ts = self.get_ts(pair, time0, time1, key, mode)
        self.logrs = [np.log(self.ts['close'][i] / self.ts['close'][i-1]) for i in range(1, len(self.ts['close']))]

    def __repr__(self) -> None:
        return f'{self.pair.upper()}: BASE -> {self.base.upper()}\tPRICE -> {self.price.upper()}'

    def get_ts(self, pair: str, start: str, end: str, key: str, mode: str = 'daily') -> dict:
        if 'KEY' not in dir():
            KEY = os.getenv('FXTOKEN')
        if mode == 'daily':
            requested = requests.get(f'https://marketdata.tradermade.com/api/v1/timeseries?currency={pair.upper()}&api_key={key}&start_date={start.upper()}&end_date={end.upper()}&format=records')
        elif mode == 'hourly':
            requested = requests.get(f'https://marketdata.tradermade.com/api/v1/timeseries?currency={pair.upper()}&api_key={key}&start_date={start.upper()}&end_date={end.upper()}&format=records&interval=hourly')
        requested = requested.json()
        try:
            quotes = requested['quotes']
            self.base = requested['base_currency']
            self.price = requested['quote_currency']
        except KeyError:
            print(f'*!* TIMESERIES NOT LOADED *!*\nresponse: {requested["message"]}')
            return None
        data = {col:[] for col in quotes[0].keys()}
        for quote in quotes:
            for col in quote:
                data[col].append(quote[col])
        return data

if __name__ == '__main__':

    eur = Pair('EURUSD')
    print(eur)
    pd.DataFrame(eur.ts)

    from matplotlib import pyplot as plt
    print(eur.logrs)
    plt.plot(eur.ts['date'], eur.ts['close'])
    plt.show()