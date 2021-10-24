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

expiration_dates = [ql.Date(30,12,2021), ql.Date(30,1,2022), ql.Date(28,2,2022), ql.Date(30,3,2022) ]
strikes = [11400.0, 11450.0, 11500.0, 11550.0, 11600.0, 11650.0, 11700.0, 11750.0, 11800.0, 11850.0]
data = [
[0.0248, 0.0205, 0.0164, 0.0128, 0.0096, 0.0070, 0.0049, 0.0033, 0.0022, 0.0014],
[0.0250, 0.0211, 0.0176, 0.0144, 0.0115, 0.0091, 0.0070, 0.0053, 0.0040, 0.0030],
[0.0265, 0.0229, 0.0195, 0.0164, 0.0136, 0.0111, 0.0090, 0.0072, 0.0057, 0.0044],
[0.0280, 0.0245, 0.0211, 0.0181, 0.0153, 0.0128, 0.0106, 0.0087, 0.0071, 0.0057]]

implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data[j][i]

black_var_surface = ql.BlackVarianceSurface(
    calculation_date, calendar, 
    expiration_dates, strikes, 
    implied_vols, day_count)

strike = 11650
expiry = 1/12 # years
print(black_var_surface.blackVol(expiry, strike))

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
one_year_idx = 2 # 12th row in data is for 1 year expiry
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
    print("%15.2f %14.5f %15.5f %20.7f " % (
        strikes[i], opt.marketValue(), 
        opt.modelValue(), 
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)
print("-"*70)
print("Average Abs Error (%%) : %5.3f" % (avg))