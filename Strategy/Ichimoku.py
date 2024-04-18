# Buy long position
def buy_long_condition(row):
    if(row['lagging_span_above_a'] and row['lagging_span_above_b'] and (row['senkou_span_b'] > row['senkou_span_a'])):
        return row['close'] > row['senkou_span_a'] and row['close'] > row['senkou_span_b']
    else:
        False

# Close long position -> sell short position with same quantity
def close_long_condition(row):
    return row['close'] < row['senkou_span_a'] or row['close'] < row['senkou_span_b']

# Sell short position
def sell_short_condition(row):
    if(row['lagging_span_below_a'] and row['lagging_span_below_b'] and (row['senkou_span_a'] > row['senkou_span_b'])):
        return row['close'] < row['senkou_span_a'] and row['close'] < row['senkou_span_b']
    else:
        False

# Close short position -> buy long position with same quantity
def close_short_condition(row):
    return row['close'] > row['senkou_span_a'] or row['close'] > row['senkou_span_b']