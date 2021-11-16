import QuantLib as ql
import pandas as pd
import numpy as np
import csv


Data = pd.read_csv("Project\FR\OpFuData.csv", header=0, index_col="date")
Data.index = pd.to_datetime(Data.index, format="%Y/%m/%d") # dtype = 'datetime64[ns]'로 나오고 1926-07-01처럼 일도 나옴
Data.index = Data.index.to_period("d") # dtype='period[M]'으로 나오고 1926-07까지 나옴 / to_period를 쓰기 위해서 to_datetime으로 바꾼 뒤 사용
print(Data)


valuationDate = ql.Date(3, 11, 2021) # 바꿔야돼!
expiryDate = ql.Date(3, 12, 2021)
strikePrice = 1.1650
underlying_qt = ql.SimpleQuote(1.16200) # 바꿔야돼!
foreignrate_qt = ql.SimpleQuote(-0.006659) 
riskfreerate_qt = ql.SimpleQuote(0.00046)
volatility_qt = ql.SimpleQuote(0.0461) 
mkt_price = 0.005 # 바꿔야돼!
option_type = ql.Option.Call # 바꿔야돼!

ql.Settings.instance().evaluationDate = valuationDate
calendar = ql.UnitedStates()
dayCount = ql.ActualActual()

u_qhd = ql.QuoteHandle(underlying_qt)
q_qhd = ql.QuoteHandle(foreignrate_qt)
r_qhd = ql.QuoteHandle(riskfreerate_qt)
v_qhd = ql.QuoteHandle(volatility_qt)

r_ts = ql.FlatForward(valuationDate, r_qhd, dayCount)
d_ts = ql.FlatForward(valuationDate, q_qhd, dayCount)
v_ts = ql.BlackConstantVol(valuationDate, calendar, v_qhd, dayCount)

r_thd = ql.YieldTermStructureHandle(r_ts)
d_thd = ql.YieldTermStructureHandle(d_ts)
v_thd = ql.BlackVolTermStructureHandle(v_ts)

process = ql.BlackScholesMertonProcess(u_qhd, d_thd, r_thd, v_thd)
engine = ql.AnalyticEuropeanEngine(process)
exercise = ql.EuropeanExercise(expiryDate)
payoff = ql.PlainVanillaPayoff(option_type, strikePrice)
option = ql.VanillaOption(payoff, exercise)
option.setPricingEngine(engine)

# implied volatility
# implied_volaitility = option.impliedVolatility(mkt_price, process)
# volatility_qt.setValue(implied_volaitility)
# print(implied_volaitility)
print('Option Premium = ', option.NPV())
print('Option Delta = ', option.delta())
print('Option Gamma = ', option.gamma())
print('Option Theta = ', option.thetaPerDay())
print('Option Vega = ', option.vega() / 100)
print('Option Rho = ', option.rho() / 100)
print('\n')