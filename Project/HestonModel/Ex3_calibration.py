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

# https://www.cmegroup.com/markets/fx/g10/euro-fx.quotes.options.html#optionProductId=8116&strikeRange=ALL&expiration=8116-X1&overrideFuture=6EX1

strikes = [1.10000, 1.11000, 1.12000, 1.13000, 1.14000, 1.15000, 1.16000]
data = [
[0.0570, 0.0471, 0.0373, 0.0278, 0.0190, 0.0115, 0.0060],
[0.0601, 0.0504, 0.0409, 0.0319, 0.0236, 0.0164, 0.0105],
[0.0605, 0.0510, 0.0419, 0.0333, 0.0254, 0.0185, 0.0129],
[0.0611, 0.0519, 0.0430, 0.0346, 0.0270, 0.0202, 0.0146],
[0.0643, 0.0553, 0.0466, 0.0384, 0.0308, 0.0239, 0.0180],
[0.0657, 0.0569, 0.0485, 0.0405, 0.0331, 0.0264, 0.0205],
[0.0664, 0.0577, 0.0494, 0.0416, 0.0343, 0.0277, 0.0218],
[0.0699, 0.0613, 0.0530, 0.0451, 0.0377, 0.0310, 0.0251],
[0.0706, 0.0621, 0.0539, 0.0461, 0.0389, 0.0323, 0.0264],
[0.0713, 0.0629, 0.0549, 0.0473, 0.0402, 0.0337, 0.0278],
[0.0750, 0.0666, 0.0585, 0.0508, 0.0436, 0.0370, 0.0310],
[0.0765, 0.0683, 0.0604, 0.0529, 0.0459, 0.0394, 0.0334],
[0.0814, 0.0733, 0.0656, 0.0582, 0.0513, 0.0447, 0.0387],
[0.0872, 0.0792, 0.0715, 0.0642, 0.0572, 0.0507, 0.0445],
[0.0916, 0.0836, 0.0760, 0.0687, 0.0617, 0.0551, 0.0489]]

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