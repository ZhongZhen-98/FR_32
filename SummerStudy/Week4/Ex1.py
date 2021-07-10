import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
import mpl_finance
import matplotlib.dates as mpl_dates

index = "005930.KS"

start = dt.datetime(2020, 7, 1)
end = dt.datetime(2021, 7, 1)

df = yf.Ticker(index)
df = df.history(start=start, end=end)

df = df[df['Volume'] != 0]

fig, ax = plt.subplots(figsize=(12,8))

ma5 = df['Close'].rolling(window=5).mean()
ma20 = df['Close'].rolling(window=20).mean()

df.insert(len(df.columns), "ma5", ma5)
df.insert(len(df.columns), "ma20", ma20)

df['Date'] = df.index
df['Date'] = df['Date'].apply(mpl_dates.date2num)
df_val = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]

golden = []
dead = []

# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(df_val)

for i in range(20, len(df)):
    if df["ma5"][i-1] <= df["ma20"][i-1] and df["ma5"][i] > df["ma20"][i]:
        golden.append(i)
    if df["ma5"][i-1] >= df["ma20"][i-1] and df["ma5"][i] < df["ma20"][i]:
        dead.append(i)

mpl_finance.candlestick_ohlc(ax, df_val.values, colorup='red', colordown='blue')
ax.plot(df["ma5"], color="green", label="MA5", marker="^", markevery=golden, markersize=12)
ax.plot(df["ma20"], color="yellow", label="MA20", marker="v", markevery=dead, markersize=12)

date_format  = mpl_dates.DateFormatter('%d %b %Y')

ax.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
fig.tight_layout()

ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('5-20 Golden/Dead Cross')
plt.legend(loc="best")
plt.show()