## http://gouthamanbalaraman.com/blog/volatility-smile-heston-model-calibration-quantlib-python.html

import QuantLib as ql
import math
import pandas as pd
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm

KOSPI200 = pd.read_csv('SummerStudy\Project\HestonModel\KOSPI_200_option.csv', dtype=object)
KOSPI200 = KOSPI200.drop(['종목명'], axis=1)
Strike = [400.0, 410.0, 420.0, 430.0, 440.0]
Edate = ['202109', '202110', '202111', '202112']
KOSPI200CP = KOSPI200
KOSPI200CP = KOSPI200CP.set_index(KOSPI200['콜 풋']).drop(['콜 풋'], axis=1)
KOSPI200C = KOSPI200CP[:'C']
KOSPI200P = KOSPI200CP['P':]
KOSPI200CD = KOSPI200C.set_index(KOSPI200C['만기일']).drop(['만기일'], axis=1)
KOSPI200PD = KOSPI200P.set_index(KOSPI200P['만기일']).drop(['만기일'], axis=1)
DateCount = len(Edate)
StrikeCount = len(Strike)
data = np.zeros((DateCount, StrikeCount))
for i in range(DateCount):
  s1 = "KOSPI200C{} = KOSPI200CD['{}':'{}']".format(Edate[i],Edate[i],Edate[i])
  exec(s1)
  s2 = "KOSPI200C{} = KOSPI200C{}.set_index(KOSPI200C{}['strike']).drop(['strike'], axis=1)".format(Edate[i],Edate[i],Edate[i])
  exec(s2)
  for j in range(StrikeCount):
    s3 = "data[{}, {}] = KOSPI200C{}['{}':'{}']['EUREX 정산가'].values".format(i, j, Edate[i], Strike[j], Strike[j])
    exec(s3)

print(data)

day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(6, 11, 2015)

spot = 416.06
ql.Settings.instance().evaluationDate = calculation_date

dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))
risk_free_rate = 0.01
dividend_rate = 0.0
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

expiration_dates = [ql.Date(14,9,2021), ql.Date(14,10,2021), ql.Date(14,11,2021), ql.Date(14,12,2021)]
strikes = [400.0, 410.0, 420.0, 430.0, 440.0]

implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data[j][i]

black_var_surface = ql.BlackVarianceSurface(
    calculation_date, calendar, 
    expiration_dates, strikes, 
    implied_vols, day_count)

# strike = 445
# expiry = 0.25 # years
# print(black_var_surface.blackVol(expiry, strike))

# dummy parameters
v0 = 0.01; kappa = 0.2; theta = 0.02; rho = -0.75; sigma = 0.5;

process = ql.HestonProcess(flat_ts, dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(spot)), 
                           v0, kappa, theta, sigma, rho)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model) 
# engine = ql.FdHestonVanillaEngine(model)

heston_helpers = []
black_var_surface.setInterpolation("bicubic")
one_year_idx = 3 # 12th row in data is for 1 year expiry (하려는 개월 수 - 1) 
date = expiration_dates[one_year_idx]
for j, s in enumerate(strikes):
    t = (date - calculation_date )
    p = ql.Period(t, ql.Days)
    sigma = data[one_year_idx][j]
    #sigma = black_var_surface.blackVol(t/365.25, s)
    helper = ql.HestonModelHelper(p, calendar, spot, s, 
                                  ql.QuoteHandle(ql.SimpleQuote(sigma)),
                                  flat_ts, 
                                  dividend_ts)
    helper.setPricingEngine(engine)
    heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model.calibrate(heston_helpers, lm, 
                 ql.EndCriteria(500, 50, 1.0e-8,1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model.params()

print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % (theta, kappa, sigma, rho, v0))

avg = 0.0

print("%15s %15s %15s %20s"% (
    "Strikes", "Market Value", 
     "Model Value", "Relative Error (%)"))
print("="*70)
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    print("%15.2f %14.5f %15.5f %20.7f " % (
        strikes[i], opt.marketValue(), 
        opt.modelValue(), 
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)
print("-"*70)
print("Average Abs Error (%%) : %5.3f" % (avg))