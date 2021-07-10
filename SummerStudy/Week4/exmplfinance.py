import datetime as dt
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt

index = "035720.KS" # 카카오 

start = dt.datetime(2016, 7, 1)
end = dt.datetime(2021, 7, 1)

df = yf.Ticker(index)
df = df.history(start=start, end=end)

df = df[-100:] # 너무 많으면 캔들그린 뒤 선 그래프처럼 보여서 오류나옴.

mpf.plot(df, type='candle', mav=(5,20,60), volume=True, show_nontrading=True)

# 1. df는 Open, High, Low, Close 데이터가 있어야함. yahoo에서 받아오는 데이터 그대로 사용가능
# 2. mav는 이평선 그리기 기간은 마음대로, 여러개도 가능
# 3. volume은 volume
# 4. nontrading 하는 날도 표시 가능
# 기존 mpl_finance는 fig, ax처럼 크기 조절이 필요하지만 mplfinance는 df만 있으면 사용 가능
# 기존에 비해 자율성이 크게 줄어듬. 
# 기존 mpl_finance를 사용하기 위해서는 {from mplfinance.original_flavor import candlestick2_ohlc}로 대신해서 import