import pandas as pd

pd.set_option('display.max_rows', 1000)

data = {
    "low": [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102],
    "high": [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109],
    "close": [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106]
}

df = pd.DataFrame(data)

# Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
#df['period9_period_low'] = df['low'].rolling(window=9).min()
#df['period9_period_high'] = df['high'].rolling(window=9).max()
df['tenkan_sen'] = (df['low'].rolling(window=9).min() + df['high'].rolling(window=9).max()) / 2

# Kijun-sen (Base Line): (26-period high + 26-period low)/2))
#df['period26_period_low'] = df['low'].rolling(window=26).min()
#df['period26_period_high'] = df['high'].rolling(window=26).max()
df['kijun_sen'] = (df['low'].rolling(window=26).min() + df['high'].rolling(window=26).max()) / 2


# Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

# Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
df['period52_low'] = df['low'].rolling(window=52).min()
df['period52_high'] = df['high'].rolling(window=52).max()
df['senkou_span_b'] = ((df['period52_low'] + df['period52_high']) / 2).shift(26)

# Chikou: The most current closing price plotted 26 time periods behind (market memeory)
df['lagging_span'] = df['close'].shift(-26)


#print(df)

#df.to_csv('out.csv')


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
data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26)

# Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
#df['period52_low'] = df['low'].rolling(window=52).min()
#df['period52_high'] = df['high'].rolling(window=52).max()
data['senkou_span_b'] = ((data['low'].rolling(window=52).min() + data['high'].rolling(window=52).max()) / 2).shift(26)

# Chikou: The most current closing price plotted 26 time periods behind (market memeory)
data['lagging_span'] = data['close'].shift(-26)

data['lagging_span_out'] = False
#data.loc[(),'lagging_span_out'] = True

#data.dropna(inplace=True)

# Strategy
def buy_condition(row):
    #return row['EMA-st'] > row['EMA-lt'] and row['RSI'] < 70
    #if(row['tenkan_sen'].isnull() and row['kijun_sen'].isnull() and row['senkou_span_a'].isnull() and row['senkou_span_b'].isnull() ):
        return row['close'] > row['tenkan_sen'] and row['close'] > row['kijun_sen'] and row['close'] > row['senkou_span_a'] and row['close'] > row['senkou_span_b']
    #else:
        #return False
    
def sell_condition(row):
    #return row['EMA-st'] < row['EMA-lt'] and row['RSI'] > 30
    #if(row['tenkan_sen'].isnull() and row['kijun_sen'].isnull()):
        return row['close'] < row['tenkan_sen'] #and row['close'] < row['kijun_sen']
    #else:
        #return False


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


print(data)
data.to_csv('out.csv')