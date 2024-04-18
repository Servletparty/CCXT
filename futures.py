import sys
from pprint import pprint

import ccxt
from binance.client import Client

from Auth import Creds
from Account import Balance
from Exchange import Utils
from Strategy import Ichimoku

import pandas as pd
from datetime import datetime, date, timedelta
import time

authentication = Creds.Creds(futures=True).get_creds()
exchange = ccxt.binance(authentication)
exchange.setSandboxMode(True)

name_base = "BTC"
name_quote = "USDT"
symbol = name_base+name_quote
timeframe = "1h"

today = date.today()
go_back = 3 # 3 days
starting_date = float(round(time.time()))-go_back*24*3600

#mark_klines = exchange.fetch_mark_ohlcv('BTC/USDT', '1h')
index_klines = exchange.fetch_index_ohlcv('BTC/USDT', timeframe, starting_date)

data = pd.DataFrame(index_klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
# keeping only the necessary columns
data.drop(columns=data.columns.difference(['timestamp','close','low','high']), inplace=True)
# formating the index
data.set_index(data['timestamp'], inplace=True)
data.index = pd.to_datetime(data.index, unit='ms')
del data['timestamp']
# formating the numbers
data["close"] = pd.to_numeric(data["close"])
data["low"] = pd.to_numeric(data["close"])
data["high"] = pd.to_numeric(data["close"])

# Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
data['tenkan_sen'] = (data['low'].rolling(window=9).min() + data['high'].rolling(window=9).max()) / 2

# Kijun-sen (Base Line): (26-period high + 26-period low)/2))
data['kijun_sen'] = (data['low'].rolling(window=26).min() + data['high'].rolling(window=26).max()) / 2


# Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26).fillna(1000000000)

# Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
data['senkou_span_b'] = ((data['low'].rolling(window=52).min() + data['high'].rolling(window=52).max()) / 2).shift(26).fillna(1000000000)

# Chikou: The most current closing price plotted 26 time periods behind (market memory)
data['lagging_span'] = data['close'].shift(-26).fillna(0)

data['lagging_span_in_past'] = data['lagging_span'].rolling(window=27).agg(lambda rows: rows.iloc[0])
data['senkou_span_a_max'] = data['senkou_span_a'].rolling(window=27).max()
data['senkou_span_b_max'] = data['senkou_span_b'].rolling(window=27).max()
data['senkou_span_a_min'] = data['senkou_span_a'].rolling(window=27).min()
data['senkou_span_b_min'] = data['senkou_span_b'].rolling(window=27).min()

# For long position
data['lagging_span_above_a'] = data['lagging_span'].rolling(window=27).agg(lambda rows: rows.iloc[0]) > data['senkou_span_a'].rolling(window=27).max()
data['lagging_span_above_b'] = data['lagging_span'].rolling(window=27).agg(lambda rows: rows.iloc[0]) > data['senkou_span_b'].rolling(window=27).max()

# For short position
data['lagging_span_below_a'] = data['lagging_span'].rolling(window=27).agg(lambda rows: rows.iloc[0]) < data['senkou_span_a'].rolling(window=27).min()
data['lagging_span_below_b'] = data['lagging_span'].rolling(window=27).agg(lambda rows: rows.iloc[0]) < data['senkou_span_b'].rolling(window=27).min()

print(data.iloc[-1])



if Ichimoku.buy_long_condition(data.iloc[-1]):
    print("BUY LONG!!")
elif Ichimoku.close_long_condition(data.iloc[-1]):
    print("CLOSE LONG!!")
elif Ichimoku.sell_short_condition(data.iloc[-1]):
    print("SELL SHORT!!")
elif Ichimoku.close_short_condition(data.iloc[-1]):
    print("CLOSE SHORT!!")
else:
    print("DO NOTHING!!")
    
sys.exit()



balance = Balance.Balance(exchange)
print(balance.get_balance("USDT")["total"])

pair = "BTCUSDT"
order_type = "market"


positions = exchange.fetch_balance()['info']['positions']

for position in positions:
    if position['symbol'] == pair:
        print(position)


current_price = Utils.get_pair_current_price(exchange, pair)
print(current_price)
side = "sell"
amount_in_usdt = 200

amount = amount_in_usdt / current_price
print(f"> Buy: {amount} {pair} for {amount_in_usdt} $")

params = {'leverage': 1}

order = exchange.create_order(pair, order_type, side, amount, params = params)

order_id = order['id']
print(order_id)

positions = exchange.fetch_balance()['info']['positions']

for position in positions:
    if position['symbol'] == pair:
        print(position)
        side = "buy"
        amount = float(position['positionAmt'])*-1
        print(f"> Buy: {amount} BTC")
        params = {'leverage': 1}
        order = exchange.create_order(pair, order_type, side, amount, params = params)
        break
        