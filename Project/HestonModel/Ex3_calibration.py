## http://gouthamanbalaraman.com/blog/volatility-smile-heston-model-calibration-quantlib-python.html

import QuantLib as ql
import math
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm

day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(4, 10, 2021)

spot = 659.37
ql.Settings.instance().evaluationDate = calculation_date

dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))
risk_free_rate = 0.01
dividend_rate = 0.0
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

# MATRIXXX
expiration_dates = [ql.Date(3,12,2021), ql.Date(7,1,2022),
                    ql.Date(4,2,2022), ql.Date(4,3,2022), ql.Date(8,4,2022), 
                    ql.Date(6,5,2022), ql.Date(3,6,2022), ql.Date(8,7,2022),
                    ql.Date(5,8,2022), ql.Date(9,9,2022), ql.Date(7,10,2022), 
                    ql.Date(9,12,2022), ql.Date(3,3,2023),
                    ql.Date(9,6,2023), ql.Date(8,9,2023)]

strikes = [1.10000, 1.11000, 1.12000, 1.13000, 1.14000, 1.15000, 1.16000, 1.17000]
data = [
[1.63, 0.73, 0.15, 0.19, -0.53, -0.39, 0.23, 0.69],
[1.19, 0.87, 0.66, 0.68, 0.42, 0.27, 0.27, 0.35],
[1.05, 0.85, 0.63, 0.47, 0.31, 0.61, 0.50, 0.27],
[0.83, 0.57, 0.37, 0.74, 0.07, 0.03, -0.04, 0.13],
[0.66, 0.47, 0.27, 0.13, -0.03, -0.12, -0.13, -0.13],
[0.67, 0.44, 0.26, 0.12, -0.03, -0.13, -0.21, -0.21],
[0.60, 0.41, 0.24, 0.10, -0.02, -0.13, -0.19, -0.21],
[-0.08, -0.13, -0.21, -0.27, -0.33, -0.39, -0.40, -0.42],
[-0.07, -0.13, -0.18, -0.25, -0.32, -0.36, -0.41, -0.43],
[-0.04, -0.10, -0.17, -0.23, -0.30, -0.33, -0.35, -0.38],
[-0.05, -0.11, -0.17, -0.24, -0.31, -0.38, -0.43, -0.43],
[-0.05, -0.14, -0.19, -0.24, -0.31, -0.36, -0.38, -0.39]]

implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data[j][i]

black_var_surface = ql.BlackVarianceSurface(
    calculation_date, calendar, 
    expiration_dates, strikes, 
    implied_vols, day_count)

# strike = 11650
# expiry = 1/12 # years
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
one_year_idx = 11 # 12th row in data is for 1 year expiry
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

print("%15s %15s %15s %20s" % (
    "Strikes", "Market Value", 
     "Model Value", "Relative Error (%)"))
print("="*70)
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    # print("%15.2f %14.5f %15.5f %20.7f " % (
    #     strikes[i], opt.marketValue(), 
    #     opt.modelValue(), 
    #     100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)
print("-"*70)
print("Average Abs Error (%%) : %5.3f" % (avg))