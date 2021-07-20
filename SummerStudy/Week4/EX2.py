# Yahoo api

import datetime as dt
import yfinance as yf
# import mpl_finance
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# import mplfinance as mpf
from mplfinance.original_flavor import candlestick2_ohlc

index = "035720.KS" # 카카오 

start = dt.datetime(2016, 7, 1)
end = dt.datetime(2021, 7, 1)

df = yf.Ticker(index)
df = df.history(start=start, end=end)

day_list = []
name_list = []
for i, day in enumerate(df.index):
    if i % 120 == 0:
        day_list.append(i)
        name_list.append(day.strftime('%Y-%m-%d'))

# df = df.drop(columns=["Volume","Dividends","Stock Splits"], axis=1)
# mpf.plot(df[-100:], type='candle')

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

candlestick2_ohlc(ax, df['Open'], df['High'], df['Low'], df['Close'], width=0.5, colorup='r', colordown='b')
plt.show()