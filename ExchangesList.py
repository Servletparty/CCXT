# import sys
# lib_path = ["Account", "Auth", "Utils"]

# for lib in lib_path:
#     if lib not in sys.path:
#         sys.path.append(lib)
        

# for line in sys.path:
#     print(line)

import ccxt
#print(ccxt.exchanges) # print a list of all available exchange classes
#exchange = ccxt.binance()
#print(exchange.requiredCredentials)

from Auth import Creds
from Account import Balance
from Exchange import Utils

authentication = Creds.Creds().get_creds()
exchange = ccxt.binance(authentication)

balance = Balance.Balance(exchange)
print(balance.get_balance("USDT")["total"])

pair = "BTC/USDT"
current_price = Utils.get_pair_current_price(exchange, pair)
print(current_price)


############### backtest ###############

import pandas as pd
from binance.client import Client
import ta
import matplotlib.pyplot as plt

name_base = "BTC"
name_quote = "USDT"
timeframe = "1d"
starting_date = "01 january 2020"
initial_wallet = 1000
trading_fees = 0.001

# download the coin info
symbol = name_base+name_quote
info = Client().get_historical_klines(symbol, timeframe, starting_date)

# storing it into a pandas data frame
dl_data = pd.DataFrame(info, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])

# copy of the dowloaded data 
data = dl_data.copy()
# keeping only the necessary columns
data.drop(columns=data.columns.difference(['timestamp','close']), inplace=True)
# formating the index
data.set_index(data['timestamp'], inplace=True)
data.index = pd.to_datetime(data.index, unit='ms')
del data['timestamp']
# formating the numbers
data["close"] = pd.to_numeric(data["close"])

print(data)

data['EMA-st'] = ta.trend.ema_indicator(data['close'], 12)
data['EMA-lt'] = ta.trend.ema_indicator(data['close'], 18)
data['RSI'] = ta.momentum.rsi(data['close'])
data.dropna(inplace=True)
data

print(data)

# Strategy
def buy_condition(row):
    return row['EMA-st'] > row['EMA-lt'] and row['RSI'] < 70

def sell_condition(row):
    return row['EMA-st'] < row['EMA-lt'] and row['RSI'] > 30

# backtest loop
quote = initial_wallet
base = 0
orders = []
data['wallet'] = ''
data['hodl'] = ''
last_ath = 0

for index, row in data.iterrows():

    value = row['close']

    if buy_condition(row) and quote > 0:
        base = quote / value
        fee = base * trading_fees
        base -= fee
        quote = 0
        wallet = base * value
        if wallet > last_ath:
            last_ath = wallet

        orders.append({'timestamp': index,
                       'side': 'buy',
                       'price': value,
                       'base': base,
                       'quote': quote,
                       'wallet': wallet,
                       'fee': fee,
                       'drawdown': (wallet - last_ath) / last_ath,
                       })
        #print(f"Bought {name_base} at {value}$ on the {index}")

    elif sell_condition(row) and base > 0:
        fee = base * value * trading_fees
        quote = base * value - fee
        base = 0
        wallet = quote
        if wallet > last_ath:
            last_ath = wallet

        orders.append({'timestamp': index,
                       'side': 'sell',
                       'price': value,
                       'base': base,
                       'quote': quote,
                       'wallet': wallet,
                       'fee': fee,
                       'drawdown': (wallet - last_ath) / last_ath,
                       })
        #print(f"Sold {name_base} at {value}$ on the {index}")

    data.at[index, 'wallet'] = quote + base * value
    data.at[index, 'hodl'] = initial_wallet / data["close"].iloc[0] * value

orders = pd.DataFrame(orders, columns=['timestamp', 'side', 'price', 'base', 'quote', 'wallet', 'fee', 'drawdown'])

# Profits

profit_bot = ((data.iloc[-1]['wallet'] - initial_wallet)/initial_wallet) * 100
profit_hodl = ((data.iloc[-1]['hodl'] - data.iloc[0]['hodl'])/data.iloc[0]['hodl']) * 100

print(f" > Period: {data.index[0]} -> {data.index[-1]} ")
print(f" > Starting balance: {initial_wallet} {name_quote}")
print(f" > Final balance strategy: {round(data.iloc[-1]['wallet'],2)} {name_quote}")
print(f" > Final balance hodl: {round(data.iloc[-1]['hodl'],2)} {name_quote}")
print(f" > Strategy profits: {round(profit_bot,2)}%")
print(f" > Hodl profits: {round(profit_hodl,2)}%")
print(f" > Strategy/Hodl: {round(data.iloc[-1]['wallet']/data.iloc[-1]['hodl'],2)}")

plt.figure(figsize=(7, 5))
plt.plot(
    data.index,
    data["wallet"],
    label="wallet",
    color="gold",
)
plt.plot(
    data.index,
    data["hodl"],
    label="hodl",
    color="purple",
)
plt.legend(fontsize=16, loc="upper left")
plt.ylabel(f"{name_quote}", fontsize=20)
plt.xlabel("Timestamps", fontsize=20)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()


# Trades
orders['PnL'] = orders['wallet'].diff()
orders.at[0, 'PnL'] = orders.iloc[0]['wallet'] - initial_wallet
orders['PnL%'] = orders['wallet'].pct_change()*100
orders.at[0, 'PnL%'] = (orders.iloc[0]['wallet']-initial_wallet)/initial_wallet*100

n_orders = len(orders.index)
n_buy_orders = orders['side'].value_counts()['buy']
n_sell_orders = orders['side'].value_counts()['sell']

orders.loc[orders['side']=='buy','PnL'] = None
orders.loc[orders['side']=='buy','PnL%'] = None
orders['Win'] = ''
orders.loc[orders['PnL']>0,'Win'] = 'Yes'
orders.loc[orders['PnL']<=0,'Win'] = 'No'
n_pos_trades = orders['Win'].value_counts()['Yes']
n_neg_trades = orders['Win'].value_counts()['No']
winrate = round(n_pos_trades / (n_pos_trades+n_neg_trades) * 100,2)
avg_trades = round(orders['PnL%'].mean(),2)
avg_pos_trades = round(orders.loc[orders['Win'] == 'Yes']['PnL%'].mean(),2)
avg_neg_trades = round(orders.loc[orders['Win'] == 'No']['PnL%'].mean(),2)
best_trade = orders['PnL%'].max()
when_best_trade = orders['timestamp'][orders.loc[orders['PnL%'] == best_trade].index.tolist()[0]]
best_trade = round(best_trade,2)
worst_trade = orders['PnL%'].min()
when_worst_trade = orders['timestamp'][orders.loc[orders['PnL%'] == worst_trade].index.tolist()[0]]
worst_trade = round(worst_trade,2)

print(f" > Orders: {n_orders} ({n_buy_orders} buy, {n_sell_orders} sell)")
print(f" > Number of trades: {n_pos_trades+n_neg_trades}")
print(f" > Winrate: {winrate}%")
print(f" > Average trade profits: {avg_trades}%")
print(f" > Number of positive trades: {n_pos_trades}")
print(f" > Number of negative trades: {n_neg_trades}")
print(f" > Average of positive trades: {avg_pos_trades}%")
print(f" > Average of negative trades: {avg_neg_trades}%")
print(f" > Best trade: {best_trade}% on the {when_best_trade}")
print(f" > Worst trade: {worst_trade}% on the {when_worst_trade}")

# Drawdown
worst_drawdown = round(orders['drawdown'].min()*100,2)
print(f" > Worst: {worst_drawdown}%")

# Fees
total_fee = round(orders['fee'].sum(),2)
print(f" > Total: {total_fee} {name_quote}")